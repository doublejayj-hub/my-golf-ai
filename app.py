import streamlit as st
import streamlit.components.v1 as components
import base64
import google.generativeai as genai

# [1] Gemini 보안 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"API 인증 오류: {e}")
    st.stop()

# [2] 분석 엔진 (데이터 전송 인터페이스 최적화)
HTML_TEMPLATE = """
<div style="width:100%; background:#000; border-radius:12px; overflow:hidden; position:relative; border: 1px solid #333;">
    <video id="v" controls playsinline style="width:100%; display:block; height:auto;"></video>
    <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
    <div style="position:absolute; bottom:50px; left:0; width:100%; background:rgba(0,0,0,0.8); color:#0f0; padding:8px 15px; font-family:monospace; z-index:100; display:flex; justify-content:space-between; font-size:14px; border-top:1px solid #0f0;">
        <span>VIEW: LABEL_HERE</span>
        <span>SPINE DELTA: <b id="d_v">0.0</b>°</span>
    </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils"></script>
<script>
    const v=document.getElementById('v'), c=document.getElementById('c'), ctx=c.getContext('2d'), dD=document.getElementById('d_v');
    let maxS=0, minS=180;
    const pose=new Pose({locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${p}`});
    pose.setOptions({modelComplexity:1, smoothLandmarks:true, minDetectionConfidence:0.5, minTrackingConfidence:0.5});
    
    pose.onResults((r)=>{
        if(!r.poseLandmarks) return;
        c.width=v.videoWidth; c.height=v.videoHeight;
        ctx.save(); ctx.clearRect(0,0,c.width,c.height);
        const sh=r.poseLandmarks[11], h=r.poseLandmarks[23];
        const spine = Math.abs(Math.atan2(h.y-sh.y, h.x-sh.x)*180/Math.PI);
        
        if(spine > 0) {
            if(spine > maxS) maxS = spine; 
            if(spine < minS) minS = spine;
            const currentDelta = (maxS - minS).toFixed(1);
            dD.innerText = currentDelta;

            // [핵심] 1초마다 서버에 강제 신호 전송
            if(v.currentTime % 1 < 0.1) {
                window.parent.postMessage({
                    type: 'streamlit:set_query_params', 
                    query_params: {s_delta: currentDelta, timestamp: Date.now()}
                }, '*');
            }
        }
        drawConnectors(ctx,r.poseLandmarks,POSE_CONNECTIONS,{color:'#00FF00',lineWidth:3});
        ctx.restore();
    });

    v.src = "VIDEO_DATA_URI";
    v.onplay = async function(){ 
        while(!v.paused && !v.ended){ await pose.send({image:v}); await new Promise(r=>requestAnimationFrame(r)); } 
    };
</script>
"""

st.set_page_config(layout="wide", page_title="GDR AI Pro v14")
st.title("⛳ Gemini Pro 지능형 리포트 (데이터 동기화 강화)")

# 데이터 수신 및 세션 저장
qp = st.query_params
s_delta = float(qp.get("s_delta", 0.0))

tab1, tab2 = st.tabs(["🎥 분석 센터", "🤖 Gemini 심층 리포트"])

with tab1:
    f = st.file_uploader("영상을 업로드하세요", type=['mp4', 'mov'])
    if f:
        v_src = "data:video/mp4;base64," + base64.b64encode(f.read()).decode()
        components.html(HTML_TEMPLATE.replace("VIDEO_DATA_URI", v_src).replace("LABEL_HERE", "SWING"), height=500)
        if s_delta > 0:
            st.success(f"✅ 데이터 수신 중: 현재 편차 {s_delta}° (리포트 탭을 확인하세요)")

with tab2:
    st.header("📋 AI 실시간 역학 분석 리포트")
    
    if s_delta > 0.1:
        st.write(f"📊 **추출된 물리 데이터**: 척추각 변화량 {s_delta}°")
        
        # 중복 호출 방지를 위해 세션 상태 활용
        if st.button("🔄 Gemini 분석 시작/갱신"):
            with st.spinner("Gemini Pro가 데이터를 정밀 분석 중입니다..."):
                try:
                    prompt = f"""
                    당신은 전문 골프 역학 코치입니다. 현재 골퍼의 척추각 편차 데이터는 {s_delta}도입니다.
                    이 수치를 기반으로 스윙의 안정성을 분석하고, 배치기(Early Extension) 여부를 진단하세요.
                    마지막엔 6월에 아빠가 될 골퍼를 위해 격려의 말을 남겨주세요.
                    """
                    response = model.generate_content(prompt)
                    st.markdown("### 🤖 Gemini 분석 결과")
                    st.write(response.text)
                    
                    st.divider()
                    st.subheader("📺 추천 교정 레슨")
                    st.video("https://www.youtube.com/watch?v=VrOGGXdf_tM" if s_delta > 4 else "https://www.youtube.com/watch?v=2vT64W2XfC0")
                except Exception as e:
                    st.error(f"리포트 생성 중 오류: {e}")
    else:
        st.warning("⚠️ **분석 데이터가 아직 없습니다.**")
        st.info("영상을 재생하면 실시간으로 척추각 데이터가 수집됩니다. 데이터 수집이 확인되면 버튼이 나타납니다.")

st.sidebar.markdown("**Baby Due: June 2026** 👶")
