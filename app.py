import streamlit as st
import base64
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="GDR AI Pro v124")
st.title("⛳ GDR AI Pro: 골든 버전 복구 및 가이드라인 고정 v124.0")

def get_stable_engine(f_v64, s_v64):
    return f"""
    <style>
        .v-box {{ position: relative; background: #000; padding: 0; border-radius: 12px; border: 1px solid #333; margin-bottom: 25px; overflow: hidden; }}
        video {{ width: 100%; display: block; z-index: 1; }}
        canvas {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 2; }}
        .val-disp {{ margin-top:10px; color:#0f0; font-family:monospace; font-size:26px; font-weight:bold; background:rgba(0,0,0,0.8); padding:15px; border-radius:8px; border:1px solid #0f0; text-align:center; }}
    </style>

    <div class="v-box">
        <video id="vf" controls playsinline muted></video>
        <canvas id="fc"></canvas>
        <div class="val-disp">Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°</div>
    </div>

    <div class="v-box">
        <video id="vs" controls playsinline muted></video>
        <canvas id="sc"></canvas>
        <div class="val-disp">Δ Spine: <span id="s_sp">0.0</span>° | Knee: <span id="s_kn">0.0</span>°</div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs');
        const fctx=document.getElementById('fc').getContext('2d');
        const sctx=document.getElementById('sc').getContext('2d');
        let pose = null, f_d = {{}}, s_d = {{}};

        function initPose() {{
            if(pose) return; 
            pose = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
            pose.setOptions({{modelComplexity:1, smoothLandmarks:true, minDetectionConfidence:0.5}});
            pose.onResults(onResults);
        }}

        function drawWall(ctx, canv, x, color) {{
            ctx.setLineDash([10, 10]);
            ctx.beginPath();
            ctx.moveTo(x * canv.width, 0);
            ctx.lineTo(x * canv.width, canv.height);
            ctx.strokeStyle = color; ctx.lineWidth = 4; ctx.stroke();
            ctx.setLineDash([]);
        }}

        function onResults(r) {{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            
            // 1. [정면] 골든 버전 로직 + 왼발 벽 (lm[28])
            if (!vf.paused && !f_d.lock) {{
                const fc=document.getElementById('fc');
                fc.width = vf.offsetWidth; fc.height = vf.offsetHeight;
                fctx.clearRect(0, 0, fc.width, fc.height);
                f_d.c = (f_d.c || 0) + 1;

                // 정면 왼발 벽: 골퍼 기준 왼발 = 시청자 기준 화면 오른쪽(lm[28])
                if (f_d.c <= 15) f_d.wallX = lm[28].x;
                if (f_d.wallX) drawWall(fctx, fc, f_d.wallX, '#00ff00');

                let curCX = (lm[24].x + lm[23].x) / 2;
                if(!f_d.stCX) f_d.stCX = curCX;
                document.getElementById('f_sw').innerText = Math.max(0, ((f_d.stCX - curCX)/0.1)*100).toFixed(1);
            }}

            // 2. [측면] 골든 버전 로직 + 엉덩이 끝선
            if (!vs.paused && !s_d.lock) {{
                const sc=document.getElementById('sc');
                sc.width = vs.offsetWidth; sc.height = vs.offsetHeight;
                sctx.clearRect(0, 0, sc.width, sc.height);
                s_d.c = (s_d.c || 0) + 1;

                // 엉덩이 끝선: 어드레스 시 골반 좌표 중 가장 오른쪽(등 뒤) 값
                if (s_d.c <= 15) s_d.buttX = Math.max(lm[23].x, lm[24].x);
                if (s_d.buttX) drawWall(sctx, sc, s_d.buttX, '#0000ff');

                const hC = {{x:(lm[23].x+lm[24].x)/2, y:(lm[23].y+lm[24].y)/2}};
                const sC = {{x:(lm[11].x+lm[12].x)/2, y:(lm[11].y+lm[12].y)/2}};
                const curSp = Math.abs(Math.atan2(hC.y - sC.y, hC.x - sC.x) * 180/Math.PI);
                if (s_d.c === 10) s_d.addr = {{s:sC, h:hC, ang:curSp}};
                if (s_d.addr) {{
                    sctx.beginPath();
                    sctx.moveTo(s_d.addr.s.x * sc.width, s_d.addr.s.y * sc.height);
                    sctx.lineTo(s_d.addr.h.x * sc.width, s_d.addr.h.y * sc.height);
                    sctx.strokeStyle = '#00f'; sctx.lineWidth = 2; sctx.stroke();
                }}
            }}
        }}

        async function loop(v) {{
            v.playbackRate = 0.2;
            while(!v.paused && !v.ended) {{
                await pose.send({{image: v}});
                await new Promise(r => setTimeout(r, 50));
            }}
        }}

        vf.onplay = () => {{ initPose(); f_d = {{c:0}}; loop(vf); }};
        vs.onplay = () => {{ initPose(); s_d = {{c:0}}; loop(vs); }};

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
    </script>
    """

f_file = st.file_uploader("Front Video", type=['mp4', 'mov'])
s_file = st.file_uploader("Side Video", type=['mp4', 'mov'])

if f_file and s_file:
    f_b = base64.b64encode(f_file.read()).decode()
    s_b = base64.b64encode(s_file.read()).decode()
    components.html(get_stable_engine(f_b, s_b), height=1500)
