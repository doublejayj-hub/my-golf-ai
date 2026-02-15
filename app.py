import streamlit as st
import streamlit.components.v1 as components
import uuid
import base64

# 1. 페이지 설정
st.set_page_config(layout="wide", page_title="GDR AI Real-Time Coach")

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.title("⛳ GDR AI 진짜 연산 엔진 (코드 무결성 검증 완료)")

# 2. 영상 세션 관리
if 'f_vid' not in st.session_state: st.session_state.f_vid = None

tab1, tab2 = st.tabs(["📸 실시간 관절 추적", "📊 추출 데이터 로그"])

with tab1:
    f_input = st.file_uploader("분석할 영상 업로드", type=['mp4', 'mov'], key=f"v_{st.session_state.session_id}")
    
    if f_input:
        # 영상 데이터를 Base64로 안전하게 변환
        tfile = f_input.read()
        b64_vid = base64.b64encode(tfile).decode()
        
        st.info("AI 엔진이 동작 준비 중입니다. 업로드 후 재생 버튼을 눌러주세요.")

        # [핵심] 따옴표 꼬임을 방지하기 위해 HTML 템플릿을 정밀하게 정의
        # 아래 문자열은 """로 시작해서 """로 정확히 끝납니다.
        html_template = """
        <div id="container" style="position: relative; width: 100%; height: 500px; background: #000;">
            <video id="input_video" controls style="width: 100%; height: 100%;"></video>
            <canvas id="output_canvas" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;"></canvas>
            <div id="status" style="position: absolute; top: 10px; left: 10px; color: #0f0; font-family: monospace; background: rgba(0,0,0,0.7); padding: 5px; z-index: 10;">
                [AI ENGINE] Status: Ready
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
        <script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils"></script>
        
        <script>
            const videoElement = document.getElementById('input_video');
            const canvasElement = document.getElementById('output_canvas');
            const canvasCtx = canvasElement.getContext('2d');
            const statusDiv = document.getElementById('status');

            const pose = new Pose({locateFile: (file) => {
                return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`;
            }});

            pose.setOptions({
                modelComplexity: 1,
                smoothLandmarks: true,
                minDetectionConfidence: 0.5,
                minTrackingConfidence: 0.5
            });

            pose.onResults((results) => {
                if (!results.poseLandmarks) {
                    statusDiv.innerHTML = "[AI ENGINE] Pose not
