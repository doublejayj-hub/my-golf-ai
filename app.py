import streamlit as st
import streamlit.components.v1 as components
import uuid

# 1. 페이지 설정
st.set_page_config(layout="wide", page_title="GDR AI Real-Time Coach")

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.title("⛳ GDR AI 진짜 연산 엔진 (프레임 연동 버전)")

# 2. 영상 세션 관리
if 'f_vid' not in st.session_state: st.session_state.f_vid = None

tab1, tab2 = st.tabs(["📸 실시간 관절 추적", "📊 추출 데이터 로그"])

with tab1:
    f_input = st.file_uploader("분석할 영상 업로드", type=['mp4', 'mov'], key=f"v_{st.session_state.session_id}")
    
    if f_input:
        # 파일 바이너리 데이터를 JS로 넘겨주기 위해 임시 저장 및 데이터 처리
        import base64
        tfile = f_input.read()
        b64_vid = base64.b64encode(tfile).decode()
        
        st.info("AI 엔진에 영상을 로드 중입니다. 잠시만 기다려주세요...")

        components.html(
            f"""
            <div id="container" style="position: relative; width: 100%; height: 500px; background: #000;">
                <video id="input_video" controls style="width: 100%; height: 100%;"></video>
                <canvas id="output_canvas" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;"></canvas>
                <div id="status" style="position: absolute; top: 10px; left: 10px; color: #0f0; font-family: monospace; background: rgba(0,0,0,0.7); padding: 5px; z-index: 10;">
                    [AI ENGINE] Status: Loading Video...
                </div>
            </div>

            <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
            <script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils"></script>
            
            <script>
                const videoElement = document.getElementById('input_video');
                const canvasElement = document.getElementById('output_canvas');
                const canvasCtx = canvasElement.getContext('2d');
                const statusDiv = document.getElementById('status');

                // 1. MediaPipe 설정
                const pose = new Pose({{locateFile: (file) => {{
                    return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{file}}`;
                }}}});

                pose.setOptions({{
                    modelComplexity: 1,
                    smoothLandmarks: true,
                    minDetectionConfidence: 0.5,
                    minTrackingConfidence: 0.5
                }});

                pose.onResults((results) => {{
                    if (!results.poseLandmarks) {{
                        statusDiv.innerHTML = "[AI ENGINE] Pose not detected";
                        return;
                    }
                    statusDiv.innerHTML = "[AI ENGINE] Tracking 33 Landmarks - ACTIVE";
                    
                    canvasCtx.save();
                    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
                    
                    // 캔버스 크기를 영상 해상도에 맞춤
                    canvasElement.width = videoElement.videoWidth;
                    canvasElement.height = videoElement.videoHeight;
                    
                    // 관절 뼈대 그리기
