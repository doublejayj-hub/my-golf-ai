import streamlit as st
import streamlit.components.v1 as components
import base64
import google.generativeai as genai

# [1] 보안 연동: Secrets에서 API 키 호출
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # 유료 티어의 성능을 활용
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception:
    st.error("Secrets 설정에서 'GEMINI_API_KEY'를 확인해주세요.")
    st.stop()

# [2] 통합 분석 엔진 (가장 안정적인 치환 방식)
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
        if(spine > maxS) maxS = spine; if(spine < minS) minS = spine;
        sD.innerText = spine.toFixed(1);

        if(v.currentTime > 1 && v.currentTime % 2 < 0.1) {
            window.parent.postMessage({
                type: 'streamlit:set_query_params', 
                query_params: {s_delta: (maxS-minS).toFixed(1)}
            }, '*');
        }
        drawConnectors(ctx,r.poseLandmarks,POSE_CONNECTIONS,{color:'#00FF00',lineWidth:3});
        ctx.restore();
    });

    // 비디오 데이터 안전 주입
    v.src = "VIDEO_DATA_URI";
    v.onplay = async function(){ 
        while(!v.paused && !v.ended){ await pose.send({image:v}); await new Promise(r=>requestAnimationFrame(r)); } 
    };
</script>
"""

st.set_page_config(layout="wide", page_title="GDR AI Pro")
st.title("⛳ Gemini Pro 지능형 골프 대시보드 v12.5")

# 실시간 분석 데이터 수신
qp = st.query_params
s_delta = float(qp.get("s_delta", 0.0))

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
    st.header("📋 AI 실시간 역학 분석 (Powered by Gemini)")
    if (f_f or f_s) and s_delta > 0:
        with st.spinner("Gemini Pro가 실제 데이터를 분석 중입니다..."):
            prompt = f"""
            당신은 세계적인 골프 코치입니다. 현재 골퍼의 척추각 편차 데이터가 {s_delta}도로 측정되었습니다.
            1. 이 수치가 의미하는 '운동학적 사슬'의 문제를 전문적으로 분석해줘.
            2. 6월에 태어날 아기에게 멋진 스윙을 보여줄 수 있도록 따뜻한 응원을 포함해줘.
            """
            response = model.generate_content(prompt)
            st.chat_message("assistant").write(response.text)
            
        st.divider()
        st.video("https://www.youtube.com/watch?v=VrOGGXdf_tM" if s_delta > 4 else "https://www.youtube.com/watch?v=2vT64W2XfC0")
    else:
        st.info("영상을 업로드하고 재생하면 실제 데이터 리포트가 생성됩니다.")

st.sidebar.markdown(f"**Baby Due: June 2026** 👶")
