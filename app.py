import streamlit as st
import streamlit.components.v1 as components
import base64

# [1] HTML/JS 엔진: 데이터 주입 경로를 '이벤트 기반'으로 변경
STABLE_HTML = """
<div id="w" style="width:100%; background:#000; border-radius:10px; overflow:hidden; position:relative;">
    <video id="v" controls playsinline style="width:100%; display:block; height:auto;"></video>
    <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
    <div id="st" style="position:absolute; top:10px; left:10px; color:#fff; background:rgba(0,123,255,0.8); padding:8px; font-family:monospace; border-radius:5px; font-weight:bold; z-index:100;">[AI] STANDBY</div>
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

    // 파이썬으로부터 데이터를 전달받는 리스너
    window.addEventListener("message", (e) => {
        if (e.data.type === "LOAD") {
            v.src = e.data.src;
            v.load();
            st.innerText = "[AI] READY TO PLAY";
        }
    });

    async function run() {
        if (!v.paused && !v.ended) { await pose.send({image: v}); }
        requestAnimationFrame(run);
    }
    v.onplay = run;
</script>
"""

st.set_page_config(layout="wide")
st.title("⛳ GDR AI 초정밀 분석기 (재생 동기화 완료)")

f = st.file_uploader("분석할 영상을 업로드하세요", type=['mp4', 'mov'])

if f:
    # 1. 영상 데이터 처리 (가장 안전한 Base64 방식 유지)
    v_b64 = base64.b64encode(f.read()).decode()
    v_src = f"data:video/mp4;base64,{v_b64}"
    
    # 2. HTML 컴포넌트 먼저 렌더링
    components.html(STABLE_HTML, height=600)
    
    # 3. [중요] 0.5초 대기 후 영상 데이터 전송 (재생기 로딩 시간 확보)
    st.markdown(f"""
        <script>
        setTimeout(() => {{
            const iframes = window.parent.document.querySelectorAll('iframe');
            iframes.forEach(iframe => {{
                iframe.contentWindow.postMessage({{type: 'LOAD', src: '{v_src}'}}, '*');
            }});
        }}, 500);
        </script>
        """, unsafe_allow_html=True)
    
    st.success("분석 엔진 로드 완료! '[AI] READY TO PLAY' 문구가 뜨면 재생 버튼을 눌러주세요.")
else:
    st.info("6월 아기 탄생 전, 최고의 스윙 시퀀스를 만들어보세요!")
