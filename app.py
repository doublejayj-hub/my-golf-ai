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

st.set_page_config(layout="wide", page_title="GDR AI Pro v17")
st.title("⛳ GDR AI Pro: 무결성 분석 대시보드 v17.0")

# [2] 통합 분석 엔진 (재생 안정성 극대화)
def get_stable_engine(v_src, label):
    return f"""
    <div style="width:100%; background:#000; border-radius:10px; overflow:hidden; position:relative; border: 2px solid #555;">
        <video id="v" controls playsinline style="width:100%; display:block; aspect-ratio:9/16; background:#000;"></video>
        <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
        <div style="position:absolute; top:10px; right:10px; background:rgba(0,0,0,0.8); color:#0f0; padding:5px 10px; font-family:monospace; z-index:100; border:1px solid #0f0; font-size:14px;">
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

# [3] 메인 레이아웃 (세로 배치로 재생 안정성 확보)
col_v1, col_v2 = st.columns(2)

with col_v1:
    st.subheader("🎥 정면 스윙 분석")
    f_f = st.file_uploader("정면 영상 업로드", type=['mp4', 'mov'], key="f_up")
    if f_f:
        v_src = "data:video/mp4;base64," + base64.b64encode(f_f.read()).decode()
        components.html(get_stable_engine(v_src, "FRONT"), height=650)

with col_v2:
    st.subheader("🎥 측면 스윙 분석")
    f_s = st.file_uploader("측면 영상 업로드", type=['mp4', 'mov'], key="s_up")
    if f_s:
        v_src = "data:video/mp4;base64," + base64.b64encode(f_s.read()).decode()
        components.html(get_stable_engine(v_src, "SIDE"), height=650)

st.divider()

# [4] 데이터 기반 지능형 리포트 섹션
st.header("📋 AI 실시간 역학 리포트 & 처방전")
col_info, col_report = st.columns([1, 2])

with col_info:
    st.info("💡 **사용 가이드**\n1. 영상을 재생하여 실시간 뼈대와 Δ(편차) 수치를 확인하세요.\n2. 확인된 Δ 수치를 아래에 입력하면 Gemini AI가 분석을 시작합니다.")
    s_delta_input = st.number_input("영상에 표시된 Δ(편차) 수치 입력", min_value=0.0, step=0.1, key="delta_val")

with col_report:
    if s_delta_input > 0:
        if st.button("🔄 Gemini AI 심층 분석 및 처방 요청"):
            with st.spinner("Gemini Pro가 분석 중입니다..."):
                prompt = f"""
                당신은 골프 역학 전문가입니다. 척추각 편차 {s_delta_input}도인 골퍼를 위해:
                1. 이 수치가 암시하는 운동학적 문제(배치기, 축 흔들림 등)를 역학 원론적으로 설명해줘.
                2. 6월에 태어날 아기에게 멋진 스윙을 보여줄 아빠를 위한 격려를 포함해줘.
                """
                response = model.generate_content(prompt)
                st.chat_message("assistant").write(response.text)
                
                # 영상 가이드 (조건부)
                yt = "https://www.youtube.com/watch?v=VrOGGXdf_tM" if s_delta_input > 4 else "https://www.youtube.com/watch?v=2vT64W2XfC0"
                st.video(yt)
    else:
        st.write("분석 수치를 입력하면 이곳에 개인화된 처방전이 나타납니다.")

st.divider()
st.subheader("📸 프로 스윙 레퍼런스 가이드")
st.image("https://img.vavel.com/tiger-woods-swing-1608144214553.jpg", caption="Tiger Woods: 척추각 고정의 정석")

st.sidebar.markdown(f"**Baby Due: June 2026** 👶")
