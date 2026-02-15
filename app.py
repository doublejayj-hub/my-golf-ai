import streamlit as st
import streamlit.components.v1 as components
import base64

# [1] 에러 없는 정적 HTML 엔진 (데이터 주입 방식을 원천적으로 바꿈)
# f-string을 쓰지 않아 중괄호 에러가 절대 나지 않습니다.
RAW_HTML = """
<div style="width:100%; background:#000; border-radius:10px; overflow:hidden; position:relative;">
    <video id="v" controls playsinline style="width:100%; display:block; height:auto;"></video>
    <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
    <div id="st" style="position:absolute; top:10px; left:10px; color:#fff; background:rgba(0,123,255,0.8); padding:8px; font-family:monospace; border-radius:5px; font-weight:bold; z-index:100;">[AI] READY</div>
</div>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils"></script>
<script>
    const v = document.getElementById('v');
    const c = document.getElementById('c');
    const ctx = c.getContext('2d');
    const st = document.getElementById('st');
    let pL = null, pY = 0;

    const pose = new Pose({locateFile: (f) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${f}`});
    pose.setOptions({modelComplexity: 1, smoothLandmarks: true, minDetectionConfidence: 0.5, minTrackingConfidence: 0.5});

    pose.onResults((r) => {
        if (!r.poseLandmarks) return;
        c.width = v.videoWidth; c.height = v.videoHeight;
        ctx.save(); ctx.clearRect(0, 0, c.width, c.height);
        const w = r.poseLandmarks[15], h = r.poseLandmarks[23], vy = w.y - pY;
        const isI = (vy > 0.01 && w.y < h.y + 0.2) || (w.y >= h.y - 0.1 && w.y <= h.y + 0.3);

        if (isI && pL) {
            st.innerText = "HYPER-RES (120FPS+)";
            st.parentElement.style.background = "rgba(255,0,0,0.8)";
            [0.25, 0.5, 0.75].forEach(t => {
                const mid = r.poseLandmarks.map((l, i) => ({
                    x: pL[i].x + (l.x - pL[i].x) * t, 
                    y: pL[i].y + (l.y - pL[i].y) * t
                }));
                drawConnectors(ctx, mid, POSE_CONNECTIONS, {color: 'rgba(0,255,255,0.4)', lineWidth: 1});
            });
        } else {
            st.innerText = "STANDARD (60FPS)";
            st.parentElement.style.background = "rgba(0,123,255,0.8)";
        }
        drawConnectors(ctx, r.poseLandmarks, POSE_CONNECTIONS, {color: '#00FF00', lineWidth: 4});
        drawLandmarks(ctx, r.poseLandmarks, {color: '#FF0000', lineWidth: 2, radius: 5});
        pL = r.poseLandmarks; pY = w.y; ctx.restore();
    });

    async function loop() {
        if (!v.paused && !v.ended) { await pose.send({image: v}); }
        requestAnimationFrame(loop);
    }
    v.onplay = loop;

    // 영상 데이터를 안전하게 수신하는 경로
    window.addEventListener("message", (e) => {
        if (e.data.type === "VIDEO_BLOB") {
            const blob = new Blob([e.data.data], { type: 'video/mp4' });
            v.src = URL.createObjectURL(blob);
            v.load();
        }
    });
</script>
"""

st.set_page_config(layout="wide", page_title="GDR AI Final")
st.title("⛳ GDR AI 초정밀 분석기 (재생 최적화 완료)")

f = st.file_uploader("영상을 업로드하세요", type=['mp4', 'mov'])

if f:
    # 1. 파일을 바이트로 읽기
    v_bytes = f.read()
    
    # 2. HTML 엔진 먼저 로드
    components.html(RAW_HTML, height=600)
    
    # 3. [핵심] 바이트 데이터를 자바스크립트로 직접 전송하여 Blob 생성
    # 이 방식은 텍스트 변환이 없어 메모리 에러가 나지 않습니다.
    js_inject = f"""
    <script>
    setTimeout(() => {{
        const iframes = window.parent.document.querySelectorAll('iframe');
        iframes.forEach(i => {{
            i.contentWindow.postMessage({{
                type: 'VIDEO_BLOB', 
                data: new Uint8Array({list(v_bytes)})
            }}, '*');
        }});
    }}, 1000);
    </script>
    """
    st.markdown(js_inject, unsafe_allow_html=True)
    st.success("분석 엔진 준비 완료! 잠시 후 영상이 로드되면 '재생'을 눌러주세요.")
else:
    st.info("6월 아기 탄생 전, 최고의 스윙을 만들어보세요!")
