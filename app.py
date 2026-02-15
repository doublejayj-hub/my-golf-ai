import streamlit as st
import streamlit.components.v1 as components
import base64

# [1] HTML/JS 엔진: 데이터 주입 방식을 '직접 주입'으로 단순화
HTML_CODE = """
<div id="wrapper" style="width:100%; background:#000; border-radius:10px; overflow:hidden; position:relative;">
    <video id="v" controls playsinline style="width:100%; display:block;"></video>
    <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
    <div id="st" style="position:absolute; top:10px; left:10px; color:#0f0; background:rgba(0,0,0,0.7); padding:5px; font-family:monospace; z-index:100;">[AI] Ready</div>
</div>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils"></script>
<script>
    const v = document.getElementById('v');
    const c = document.getElementById('c');
    const ctx = c.getContext('2d');
    const st = document.getElementById('st');

    const pose = new Pose({locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`});
    pose.setOptions({modelComplexity: 1, smoothLandmarks: true, minDetectionConfidence: 0.5, minTrackingConfidence: 0.5});

    pose.onResults((r) => {
        if (!r.poseLandmarks) return;
        c.width = v.videoWidth; c.height = v.videoHeight;
        ctx.save(); ctx.clearRect(0, 0, c.width, c.height);
        drawConnectors(ctx, r.poseLandmarks, POSE_CONNECTIONS, {color: '#00FF00', lineWidth: 4});
        drawLandmarks(ctx, r.poseLandmarks, {color: '#FF0000', lineWidth: 2, radius: 5});
        ctx.restore();
    });

    // 영상 소스를 직접 연결
    v.src = "VIDEO_DATA_URL";

    async function loop() {
        if (!v.paused && !v.ended) { 
            await pose.send({image: v}); 
        }
        requestAnimationFrame(loop);
    }
    v.onplay = () => { st.innerText = "[AI] Running..."; loop(); };
</script>
"""

st.set_page_config(layout="wide", page_title="GDR AI Final")
st.title("⛳ GDR AI 초정밀 분석기")

f = st.file_uploader("영상을 업로드하세요", type=['mp4', 'mov'])

if f:
    # 1. 영상 데이터 처리 (Base64)
    v_b64 = base64.b64encode(f.read()).decode()
    v_src = f"data:video/mp4;base64,{v_b64}"
    
    # 2. 템플릿의 소스 부분을 실제 데이터로 교체
    final_html = HTML_CODE.replace("VIDEO_DATA_URL", v_src)
    
    # 3. HTML 컴포넌트 출력
    components.html(final_html, height=600)
    st.success("업로드 완료! 재생 버튼을 누르면 분석이 시작됩니다.")
else:
    st.info("6월 육아 시작 전, 마지막 스윙 점검을 시작해볼까요?")
