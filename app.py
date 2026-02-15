import streamlit as st
import streamlit.components.v1 as components
import uuid
import base64

# 1. 페이지 설정 및 세션 초기화
st.set_page_config(layout="wide", page_title="GDR AI Real-Time Coach")

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.title("⛳ GDR AI 진짜 연산 엔진 (구문 무결성 최종 버전)")

if 'f_vid' not in st.session_state:
    st.session_state.f_vid = None

tab1, tab2 = st.tabs(["📸 실시간 관절 추적", "📊 추출 데이터 로그"])

with tab1:
    f_input = st.file_uploader("분석할 영상 업로드", type=['mp4', 'mov'], key=f"v_{st.session_state.session_id}")
    
    if f_input:
        # 영상 데이터를 Base64로 인코딩
        b64_vid = base64.b64encode(f_input.read()).decode()
        
        st.info("AI 엔진이 동작 중입니다. 재생 버튼을 눌러주세요.")

        # [해결] HTML/JS 코드를 안전하게 전달하기 위한 모듈화 방식
        # 모든 JS 로직을 하나로 합친 후, 파이썬 따옴표 이슈를 피함
        raw_html = f"""
        <div id="container" style="position:relative;width:100%;height:500px;background:#000;">
            <video id="v" controls style="width:100%;height:100%;"></video>
            <canvas id="c" style="position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;"></canvas>
            <div id="s" style="position:absolute;top:10px;left:10px;color:#0f0;font-family:monospace;background:rgba(0,0,0,0.7);padding:5px;z-index:10;">[AI] Ready</div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
        <script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils"></script>
        <script>
            const v=document.getElementById("v"), c=document.getElementById("c"), ctx=c.getContext("2d"), s=document.getElementById("s");
            const pose=new Pose({{locateFile:(f)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{f}}` bricks}});
            pose.setOptions({{modelComplexity:1,smoothLandmarks:true,minDetectionConfidence:0.5,minTrackingConfidence:0.5}});
            pose.onResults((r)=>{{
                if(!r.poseLandmarks){{s.innerText="[AI] No Pose";return;}}
                s.innerText="[AI] Active";
                c.width=v.videoWidth; c.height=v.videoHeight;
                ctx.save(); ctx.clearRect(0,0,c.width,c.height);
                drawConnectors(ctx,r.poseLandmarks,
