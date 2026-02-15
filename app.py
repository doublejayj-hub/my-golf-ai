import streamlit as st
import streamlit.components.v1 as components
import base64
import google.generativeai as genai

# [1] Gemini 보안 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception:
    st.error("Secrets 설정 오류: GEMINI_API_KEY를 확인하세요.")
    st.stop()

# [2] 원시 주입형 분석 엔진 (재생 안정성 최우선)
def get_clean_engine(v_src, label):
    return f"""
    <div style="width:100%; background:#000; border-radius:10px; overflow:hidden; position:relative;">
        <video id="v" controls playsinline style="width:100%; display:block; aspect-ratio:9/16;"></video>
        <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
        <div style="position:absolute; top:10px; right:10px; background:rgba(0,0,0,0.8); color:#0f0; padding:5px 10px; font-family:monospace; z-index:100; border:1px solid #0f0;">
            {label} | Δ <span id="d_v">0.0</span>°
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const v=document.getElementById('v'), c=document.getElementById('c'), ctx=c.getContext('2d'), dV=document.getElementById('d_v');
        let maxS=0, minS=180;
        const pose=new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` or `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:1, smoothLandmarks:true, minDetectionConfidence:0.5, minTrackingConfidence:0.5}});
        
        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            c.width=v.videoWidth; c.height=v.videoHeight;
            ctx.save(); ctx.clearRect(0,0,c.width,c.height);
            const sh=r.poseLandmarks[11], h=r.poseLandmarks[23];
            const spine = Math.abs(Math.atan2(h.y-sh.y, h.x-sh.x)*180/Math.PI);
            if(spine > 0) {{
                if(spine > maxS) maxS = spine; if(spine < minS) minS = spine;
                dV.innerText = (maxS - minS).toFixed(1);
            }}
            ctx.restore();
        }});
        v.src = "{v_src}";
        v.onplay = async function(){{ while(!v.paused && !v.ended){{ await pose.send({{image:v}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
    </script>
    """

st.set_page_config(layout="wide", page_title="GDR AI v16")
st.title("⛳ GDR AI Pro v16.0")

tab1, tab2 = st.tabs(["🎥 분석 센터", "📝 Gemini 심층 리포트"])

with tab1:
    col_f, col_s = st.columns(2)
    with col_f:
        f_f = st.file_uploader("정면 영상 업로드", type=['mp4', 'mov'], key="f_up")
        if f_f:
            v_src = "data:video/mp4;base64," + base64.b64encode(f_f.read()).decode()
            components.html(get_clean_engine(v_src, "FRONT"), height=600)

    with col_s:
        f_s = st.file_uploader("측면 영상 업로드", type=['mp4', 'mov'], key="s_up")
        if f_s:
            v_src = "data:video/mp4;base64," + base64.b64encode(f_s.read()).decode()
            components.html(get_clean_engine(v_src, "SIDE"), height=600)

with tab2:
    st.header("📋 AI 지능형 리포트")
    
    # [데이터 직결 시뮬레이션] 복잡한 통신 대신 사용자 입력을 통한 분석 트리거
    s_delta_input = st.number_input("영상에 표시된 Δ(Delta) 값을 입력하세요 (예: 5.2)", min_value=0.0, step=0.1)
    
    if s_delta_input > 0:
        if st.button("🔄 Gemini AI 정밀 분석 요청"):
            with st.spinner("Gemini Pro가 분석 중입니다..."):
                prompt = f"척추각 편차 {s_delta_input}도인 골퍼에게 6월 탄생할 아기를 언급하며 전문적인 역학 조언을 해줘."
                response = model.generate_content(prompt)
                st.chat_message("assistant").write(response.text)
                st.video("https://www.youtube.com/watch?v=VrOGGXdf_tM" if s_delta_input > 4 else "https://www.youtube.com/watch?v=2vT64W2XfC0")
    else:
        st.info("💡 분석 센터에서 영상을 재생한 후, 우측 상단에 나타나는 Δ 수치를 입력하면 심층 리포트가 생성됩니다.")

st.sidebar.markdown(f"**Baby Due: June 2026** 👶")
