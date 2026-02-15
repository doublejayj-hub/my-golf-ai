import streamlit as st
import streamlit.components.v1 as components
import base64

# [1] HTML 템플릿: 최대한 가볍고 직관적으로 재설계
HTML_TEMPLATE = """
<div id="wrapper" style="width:100%; background:#000; border-radius:10px; overflow:hidden; position:relative;">
    <video id="v" controls playsinline style="width:100%; display:block;"></video>
    <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
    <div id="msg" style="position:absolute; top:10px; left:10px; color:#0f0; background:rgba(0,0,0,0.7); padding:5px; font-family:monospace; z-index:100;">[SYSTEM] Initializing...</div>
</div>

<script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils"></script>

<script>
    const v = document.getElementById('v');
    const c = document.getElementById('c');
    const ctx = c.getContext('2d');
    const msg = document.getElementById('msg');

    const pose = new Pose({locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`});
    pose.setOptions({modelComplexity: 1, smoothLandmarks: true, minDetectionConfidence: 0.5, minTrackingConfidence: 0.5});

    pose.onResults((r) => {
        if (!r.poseLandmarks) return;
        msg.innerText = "[AI] Tracking Active";
        c.width = v.videoWidth; c.height = v.videoHeight;
        ctx.save(); ctx.clearRect(0, 0, c.width, c.height);
        drawConnectors(ctx, r.poseLandmarks, POSE_CONNECTIONS, {color: '#00FF00', lineWidth: 4});
        drawLandmarks(ctx, r.poseLandmarks, {color: '#FF0000', lineWidth: 2, radius: 5});
        ctx.restore();
    });

    v.src = "VIDEO_DATA";
    
    async function loop() {
        if (!v.paused && !v.ended) { await pose.send({image: v}); }
        requestAnimationFrame(loop);
    }
    v.onplay = () => { msg.innerText = "[AI] Running..."; loop(); };
    v.onloadedmetadata = () => { msg.innerText = "[AI] Ready to Play"; };
</script>
"""

st.set_page_config(layout="wide")
st.title("⛳ GDR AI 초정밀 분석기")

# 파일 업로더
f = st.file_uploader("영상을 선택하세요 (mp4, mov)", type=['mp4', 'mov'])

if f:
    # 데이터 처리 속도를 위해 버퍼링 최소화
    v_b64 = base64.b64encode(f.read()).decode()
    v_src = f"data:video/mp4;base64,{v_b64}"
    
    # 템플릿 결합
    app_html = HTML_TEMPLATE.replace("VIDEO_DATA", v_src)
    
    # 높이를 넉넉히 주어 모바일에서 잘리지 않게 함 [cite: image_ba6
