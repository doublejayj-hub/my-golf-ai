import streamlit as st
import streamlit.components.v1 as components
import uuid

# 1. 페이지 설정
st.set_page_config(layout="wide")

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.title("⛳ GDR AI 초정밀 분석기 (비디오 노출 보정)")

# 2. 파일 업로더
f = st.file_uploader("영상을 선택하세요 (mp4, mov)", type=['mp4', 'mov'], key=st.session_state.session_id)

if f:
    # 파일을 임시 데이터로 읽어 자바스크립트에 전달
    v_bytes = f.read()
    
    # [핵심] 가장 가벼운 HTML/JS 구조 (에러 방지를 위해 변수 치환 최소화)
    analysis_html = f"""
    <div id="wrapper" style="width:100%; height:500px; background:#000; position:relative; border-radius:10px;">
        <video id="v" controls playsinline style="width:100%; height:100%; object-fit:contain;"></video>
        <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
        <div id="status" style="position:absolute; top:10px; left:10px; color:#0f0; background:rgba(0,0,0,0.7); padding:5px; font-family:monospace; z-index:100;">[SYSTEM] Initializing...</div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils"></script>

    <script>
        const v = document.getElementById('v');
        const c = document.getElementById('c');
        const ctx = c.getContext('2d');
        const status = document.getElementById('status');

        // 1. 영상 데이터 로드 (메모리 효율적 방식)
        const blob = new Blob([new Uint8Array({list(v_bytes)})], {{ type: 'video/mp4' }});
        v.src = URL.createObjectURL(blob);

        const pose = new Pose({{locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{file}}` bricks}});
        pose.setOptions({{modelComplexity: 1, smoothLandmarks: true, minDetectionConfidence: 0.5, minTrackingConfidence: 0.5}});

        pose.onResults((r) => {{
            if (!r.poseLandmarks) return;
            c.width = v.videoWidth; c.height = v.videoHeight;
            ctx.save(); ctx.clearRect(0, 0, c.width, c.height);
            drawConnectors(ctx, r.poseLandmarks, POSE_CONNECTIONS, {{color: '#00FF00', lineWidth: 4}});
            drawLandmarks(ctx, r.poseLandmarks, {{color: '#FF0000', lineWidth
