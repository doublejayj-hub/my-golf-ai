import streamlit as st
import streamlit.components.v1 as components
import base64
import uuid

# 1. 페이지 설정
st.set_page_config(layout="wide", page_title="GDR AI Real-Time Coach")

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.title("⛳ GDR AI 분석 엔진 Phase 3.8: 정밀 임팩트 트리거")

# 2. 영상 데이터 처리
f_input = st.file_uploader("분석할 영상 업로드", type=['mp4', 'mov'], key=f"v_{st.session_state.session_id}")

if f_input:
    b64_vid = base64.b64encode(f_input.read()).decode()
    
    st.info("AI가 다운스윙 가속도를 감지하여 임팩트 순간에만 연산을 집중합니다.")

    # [Phase 3.8 핵심] 가속도 기반 임팩트 트리거 및 4배 보간
    analysis_html = f"""
    <div style="position:relative; width:100%; background:#000; border-radius:10px; overflow:hidden;">
        <video id="v" controls style="width:100%;"></video>
        <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
        <div id="vfr-panel" style="position:absolute; top:10px; left:10px; background:rgba(0,123,255,0.8); color:#fff; padding:10px; font-family:monospace; border-radius:5px; font-weight:bold; z-index:100;">
            ENGINE: <span id="vfr-status">IDLE</span>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils"></script>
    <script>
        const v = document.getElementById('v');
        const c = document.getElementById('c');
        const ctx = c.getContext('2d');
        const vfrStatus = document.getElementById('vfr-status');
        
        let prevLM = null;
        let prevWristY = 0;
        
        const pose = new Pose({{locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{file}}` bricks}});
        pose.setOptions({{modelComplexity: 1, smoothLandmarks: true, minDetectionConfidence: 0.5, minTrackingConfidence: 0.5}});
        
        function lerp(p1, p2, t) {{
            return {{ x: p1.x + (p2.x - p1.x) * t, y: p1.y + (p2.y - p1.y) * t, z: p1.z + (p2.z - p1.z) * t }};
        }}

        pose.onResults((r) => {{
            if (!r.poseLandmarks) return;
            c.width = v.videoWidth; c.height = v.videoHeight;
            ctx.save(); ctx.clearRect(0, 0, c.width, c.height);
            
            const wrist = r.poseLandmarks[15];
            const hip = r.poseLandmarks[23];
            
            // [개선된 로직] 손목의 하강 속도(v_y)와 골반 대비 위치를 결합 분석
            const wristVelocity = wrist.y - prevWristY;
            const isDownswing = wristVelocity > 0.02 && wrist.y < hip.y + 0.1; 
            const isImpactZone = wrist.y >= hip.y - 0.1 && wrist.y <= hip.y + 0.3;

            if (isDownswing || isImpactZone) {{
                vfrStatus.innerText = "HYPER-RES (120fps+)";
                vfrStatus.parentElement.style.background = "rgba(255,0,0,0.8)";
                
                if (prevLM) {{
                    [0.25, 0.5, 0.75].forEach(t => {{
                        const mid = r.poseLandmarks.map((lm, i) => lerp(prevLM[i], lm, t));
                        drawConnectors(ctx, mid, POSE_CONNECTIONS, {{color: 'rgba(0, 255, 255, 0.4)', lineWidth: 1}});
                    }});
                }}
            }} else {{
                vfrStatus.innerText = "STANDARD (60fps)";
                vfrStatus.parentElement.style.background = "rgba(0,123,255,0.8)";
            }}
            
            drawConnectors(ctx, r.poseLandmarks, POSE_CONNECTIONS, {{color: '#00FF00', lineWidth: 4}});
            drawLandmarks(ctx, r.poseLandmarks, {{color: '#FF0000', lineWidth: 2, radius: 5}});
            
            prevLM = r.poseLandmarks;
            prevWristY = wrist.y;
            ctx.restore();
        }});

        v.src = "data:video/mp4;base64,{b64_vid}";
        async function run() {{
            if (!v.paused && !v.ended) {{ await pose.send({{image: v}}); }}
            requestAnimationFrame(run);
        }}
        v.onplay = run;
    </script>
    """.replace("bricks", "")

    components.html(analysis_html, height=5
