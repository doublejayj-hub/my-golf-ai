import streamlit as st
import streamlit.components.v1 as components
import base64
import uuid

# 1. 페이지 설정 및 세션 초기화
st.set_page_config(layout="wide", page_title="GDR AI Real-Time Coach")

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.title("⛳ GDR AI 진짜 연산 엔진 (VFR 트리거 보정 버전)")

# 2. 영상 데이터 처리
f_input = st.file_uploader("분석할 영상 업로드", type=['mp4', 'mov'], key=f"v_{st.session_state.session_id}")

if f_input:
    # 영상 데이터를 Base64로 인코딩
    b_raw = f_input.read()
    b64_vid = base64.b64encode(b_raw).decode()
    
    st.info("AI가 다운스윙 가속도를 감지합니다. 재생 버튼을 눌러주세요.")

    # [해결] 괄호 꼬임을 방지하기 위해 HTML 로직을 변수로 안전하게 분리
    html_content = f"""
    <div style="position:relative; width:100%; background:#000; border-radius:10px; overflow:hidden;">
        <video id="v" controls style="width:100%;"></video>
        <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
        <div id="vfr-p" style="position:absolute; top:10px; left:10px; background:rgba(0,123,255,0.8); color:#fff; padding:10px; font-family:monospace; border-radius:5px; z-index:99;">
            MODE: <span id="vfr-s">IDLE</span>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils"></script>
    <script>
        const v = document.getElementById('v');
        const c = document.getElementById('c');
        const ctx = c.getContext('2d');
        const vfrS = document.getElementById('vfr-s');
        const vfrP = document.getElementById('vfr-p');
        
        let prevLM = null;
        let prevWY = 0;
        
        const pose = new Pose({{locateFile: (f) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{f}}` bricks}});
        pose.setOptions({{modelComplexity: 1, smoothLandmarks: true, minDetectionConfidence: 0.5, minTrackingConfidence: 0.5}});
        
        function lerp(p1, p2, t) {{
            return {{ x: p1.x + (p2.x - p1.x) * t, y: p1.y + (p2.y - p1.y) * t }};
        }}

        pose.onResults((r) => {{
            if (!r
