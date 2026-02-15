import streamlit as st
import streamlit.components.v1 as components
import base64
import google.generativeai as genai

# [1] 보안 연동: Secrets 확인
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"API 인증 오류: {e}")
    st.stop()

# [2] 통합 분석 엔진 (데이터 전송 로직 강화 버전)
HTML_TEMPLATE = """
<div style="width:100%; background:#000; border-radius:12px; overflow:hidden; position:relative; border: 1px solid #333;">
    <video id="v" controls playsinline style="width:100%; display:block; height:auto;"></video>
    <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
    <div style="position:absolute; bottom:50px; left:0; width:100%; background:rgba(0,0,0,0.7); color:#0f0; padding:8px 15px; font-family:monospace; z-index:100; display:flex; justify-content:space-between; font-size:13px; border-top:1px solid #0f0;">
        <span>VIEW: LABEL_HERE</span>
        <span>SPINE: <b id="s_v">0.0</b>°</span>
        <span id="md" style="color:#ff0;">STD</span>
    </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils"></script>
<script>
    const v=document.getElementById('v'), c=document.getElementById('c'), ctx=c.getContext('2d'), sD=document.getElementById('s_v');
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
            sD.innerText = spine.toFixed(1);
        }

        // 데이터 전송 주기 강화: 1초마다 쿼리 파라미터 갱신
        if(v.currentTime > 0.5 && Math.floor(v.currentTime * 10) % 10 === 0) {
            const delta = (maxS - minS).toFixed(1);
            if(delta > 0) {
                window.parent.postMessage({
                    type: 'streamlit:set_query_params', 
                    query_params: {s_delta: delta}
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

st.set_page_config(layout="wide", page_title="GDR AI Pro v13")
st.title("⛳ Gemini Pro 지능형 골프 리포트 v13.0")

# 실시간 분석 데이터 수신 (수치형 변환 예외 처리 강화)
qp = st.query_params
try:
    s_delta = float(qp.get("s_delta", 0.0))
except ValueError:
    s_delta = 0.0

tab1, tab2 = st.tabs(["🎥 분석 센터", "🤖 Gemini 심층 리포트"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        f_f = st.file_uploader("정면 업로드", type=['mp4', 'mov'], key="f")
        if f_f:
            v_src = "data:video/mp4;base64," + base64.b64encode(f_f.read()).decode()
            components.html(HTML_TEMPLATE.replace("VIDEO_DATA_URI", v_src).replace("LABEL_HERE", "FRONT"), height=450)
    with c2:
        f_s = st.file_uploader("측면 업로드", type=['mp4', 'mov'], key="s")
        if f_s:
            v_src = "data:video/mp4;base64," + base64.b64encode(f_s.read()).decode()
            components.html(HTML_TEMPLATE.replace("VIDEO_DATA_URI", v_src).replace("LABEL_HERE", "SIDE"), height=450)

with tab2:
    st.header("📋 AI 실시간 역학 분석 리포트")
    
    # 데이터가 0보다 클 때만 Gemini 호출 트리거
    if s_delta > 0.1:
        st.write(f"📊 **현재 감지된 척추각 편차**: {s_delta}°")
        
        with st.spinner("Gemini Pro가 데이터를 정밀 분석 중입니다..."):
            try:
                # 프롬프트에 구체적인 맥락 추가
                prompt = f"""
                당신은 세계적인 골프 물리 역학 전문가입니다. 
                현재 골퍼의 스윙 데이터: 척추각 편차 {s_delta}도.
                이 수치를 기반으로 하체 고정력과 척추 축의 안정성을 전문적으로 분석해주세요.
                또한 6월에 태어날 아기에게 자랑스러운 아빠가 될 수 있도록 따뜻한 응원을 포함해주세요.
                한국어로 답변해주세요.
                """
                response = model.generate_content(prompt)
                st.chat_message("assistant").write(response.text)
                
                st.divider()
                st.subheader("📺 추천 교정 레슨")
                yt_url = "https://www.youtube.com/watch?v=VrOGGXdf_tM" if s_delta > 4 else "https://www.youtube.com/watch?v=2vT64W2XfC0"
                st.video(yt_url)
            except Exception as e:
                st.error(f"리포트 생성 중 오류 발생: {e}")
    else:
        st.info("💡 **리포트 활성화 방법**\n1. 영상을 업로드합니다.\n2. **영상을 끝까지 또는 임팩트 구간까지 재생**합니다.\n3. 영상 하단의 'SPINE' 수치가 변하는 것을 확인한 후 이 탭을 확인하세요.")

st.sidebar.markdown(f"**Baby Due: June 2026** 👶")
