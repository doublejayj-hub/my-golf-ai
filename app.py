import streamlit as st
import streamlit.components.v1 as components
import base64
import uuid

# 1. 페이지 설정
st.set_page_config(layout="wide", page_title="GDR AI Real-Time Coach")

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.title("⛳ GDR AI 진짜 연산 엔진 (구문 무결성 최종본)")

# 2. 영상 데이터 처리
f_input = st.file_uploader("분석할 영상 업로드", type=['mp4', 'mov'], key=f"v_{st.session_state.session_id}")

if f_input:
    # 영상 데이터를 Base64로 인코딩
    b_raw = f_input.read()
    b64_vid = base64.b64encode(b_raw).decode()
    
    st.info("AI 엔진이 준비되었습니다. 영상의 재생 버튼을 눌러주세요.")

    # [해결책] f-string을 사용하지 않고 일반 문자열로 정의하여 파이썬의 개입을 원천 차단
    # 중괄호 {{}} 처리가 필요 없는 일반 문자열 방식입니다.
    html_template = """
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
        
        const pose = new Pose({locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`});
        pose.setOptions({modelComplexity: 1, smoothLandmarks: true, minDetectionConfidence: 0.5, minTrackingConfidence: 0.5});
        
        function lerp(p1, p2, t) {
            return { x: p1.x + (p2.x - p1.x) * t, y: p1.y + (p2.y - p1.y) * t };
        }

        pose.onResults((r) => {
            if (!r.poseLandmarks) return;
            c.width = v.videoWidth; c.height = v.videoHeight;
            ctx.save(); ctx.clearRect(0, 0, c.width, c.height);
            
            const wrist = r.poseLandmarks[15];
            const hip = r.poseLandmarks[23];
            const v_y = wrist.y - prevWY;
            
            // 다운스윙 가속 구간 감지 (속도 및 위치 기반)
            const isActive = (v_y > 0.01 && wrist.y < hip.y + 0.2) || (wrist.y >= hip.y - 0.1 && wrist.y <= hip.y + 0.3);

            if (isActive && prevLM) {
                vfrS.innerText = "HYPER-RES (120fps+)";
                vfrP.style.background = "rgba(255,0,0,0.8)";
                [0.25, 0.5, 0.75].forEach(t =>
