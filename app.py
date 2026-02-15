import streamlit as st
import streamlit.components.v1 as components
import base64
import uuid

# 1. 페이지 설정
st.set_page_config(layout="wide", page_title="GDR AI Real-Time Coach")

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.title("⛳ GDR AI 진짜 연산 엔진 (인프라 안정화 버전)")

# 2. 영상 업로드 섹션
f_input = st.file_uploader("분석할 영상 업로드", type=['mp4', 'mov'], key=f"v_{st.session_state.session_id}")

if f_input:
    # 영상 데이터를 Base64로 안전하게 변환
    b64_vid = base64.b64encode(f_input.read()).decode()
    
    st.info("AI 엔진이 준비되었습니다. 아래 재생 버튼을 눌러주세요.")

    # [핵심] 가장 안전한 HTML 결합 방식: 복잡한 로직을 최소화한 단일 문자열
    analysis_html = f"""
    <div style="position:relative; width:100%; background:#000;">
        <video id="v" controls style="width:100%;"></video>
        <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils"></script>
    <script>
        const v = document.getElementById('v');
        const c = document.getElementById('c');
        const ctx = c.getContext('2d');
        
        const pose = new Pose({{locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{file}}` bricks}});
        pose.setOptions({{modelComplexity: 1, smoothLandmarks: true, minDetectionConfidence: 0.5, minTrackingConfidence: 0.5}});
        
        pose.onResults((r) => {{
            if (!r.poseLandmarks) return;
            c.width = v.videoWidth; c.height = v.videoHeight;
            ctx.save(); ctx.clearRect(0, 0, c.width, c.height);
            drawConnectors(ctx, r.poseLandmarks, POSE_CONNECTIONS, {{color: '#00FF00', lineWidth: 4}});
            drawLandmarks(ctx, r.poseLandmarks, {{color: '#FF0000', lineWidth: 2, radius: 5}});
            ctx.restore();
        }});

        v.src = "data:video/mp4;base64,{b64_vid}";
        async function run() {{
            if (!v.paused && !v.ended) {{ await pose.send({{image: v}}); }}
            requestAnimationFrame(run);
        }}
        v.onplay = run;
    </script>
    """.replace("bricks", "") # 중괄호 충돌 방지용

    components.html(analysis_html, height=600)

else:
    st.warning("영상을 업로드하면 실제 관절 추적 분석이 시작됩니다.")
