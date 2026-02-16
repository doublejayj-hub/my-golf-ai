import streamlit as st
import base64
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="GDR AI Pro v121")
st.title("⛳ GDR AI Pro: 정면 세로선 교정 및 골든 로직 복구 v121.0")

def get_debugged_engine(f_v64, s_v64):
    return f"""
    <style>
        .v-box {{ position: relative; background: #000; padding: 0; border-radius: 12px; border: 1px solid #333; margin-bottom: 25px; overflow: hidden; }}
        video {{ width: 100%; display: block; z-index: 1; }}
        canvas {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 2; }}
        .val-disp {{ margin-top:10px; color:#0f0; font-family:monospace; font-size:26px; font-weight:bold; background:rgba(0,0,0,0.8); padding:15px; border-radius:8px; border:1px solid #0f0; text-align:center; }}
    </style>

    <div class="v-box">
        <h4 style="color:#0f0; margin:10px;">FRONT: 골퍼 왼발(타겟) 벽 가이드</h4>
        <video id="vf" controls playsinline muted></video>
        <canvas id="fc"></canvas>
        <div class="val-disp">Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°</div>
    </div>

    <div class="v-box">
        <h4 style="color:#0f0; margin:10px;">SIDE: 3단 척추각 오버레이</h4>
        <video id="vs" controls playsinline muted></video>
        <canvas id="sc"></canvas>
        <div class="val-disp">Δ Spine: <span id="s_sp">0.0</span>° | Knee: <span id="s_kn">0.0</span>°</div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs');
        const fc=document.getElementById('fc'), fctx=fc.getContext('2d');
        const sc=document.getElementById('sc'), sctx=sc.getContext('2d');
        let pose = null, f_d = {{}}, s_d = {{}};

        function initEngine() {{
            if(pose) {{ pose.close(); }}
            pose = new Pose({{locateFile:(p)=>`https://cdn.npm.js.net/npm/@mediapipe/pose/${{p}}` }});
            pose.setOptions({{modelComplexity:1, smoothLandmarks:true, minDetectionConfidence:0.5}});
            pose.onResults(onResults);
        }}

        // 가로/세로 선 그리기 유틸리티
        function drawVWall(ctx, canv, x, color) {{
            ctx.beginPath();
            ctx.setLineDash([10, 10]);
            ctx.moveTo(x * canv.width, 0);
            ctx.lineTo(x * canv.width, canv.height);
            ctx.strokeStyle = color;
            ctx.lineWidth = 4;
            ctx.stroke();
            ctx.setLineDash([]);
        }}

        function drawLine(ctx, canv, p1, p2, color, width=2) {{
            ctx.beginPath();
            ctx.moveTo(p1.x * canv.width, p1.y * canv.height);
            ctx.lineTo(p2.x * canv.width, p2.y * canv.height);
            ctx.strokeStyle = color;
            ctx.lineWidth = width;
            ctx.stroke();
        }}

        function onResults(r) {{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hL=lm[24], hR=lm[23], sL=lm[12], sR=lm[11], wL=lm[16], wR=lm[15];

            // 1. [정면 디버깅] 골퍼 기준 왼발(Lead Foot)은 화면상 우측인 lm[28]
            if (!vf.paused && !f_d.lock) {{
                f_d.c = (f_d.c || 0) + 1;
                fc.width = vf.offsetWidth; fc.height = vf.offsetHeight;
                fctx.clearRect(0, 0, fc.width, fc.height);

                if (f_d.c <= 10) f_d.wallX = lm[28].x; // 화면 오른쪽 발 좌표 고정
                if (f_d.wallX) drawVWall(fctx, fc, f_d.wallX, '#00ff00');

                let curCX = (hL.x + hR.x) / 2;
                if(!f_d.stCX) f_d.stCX = curCX;
                let sw = ((f_d.stCX - curCX) / 0.1) * 100;
                document.getElementById('f_sw').innerText = Math.max(0, sw).toFixed(1);
            }}

            // 2. [측면 골든 로직 복구] 척추각 오버레이
            if (!vs.paused && !s_d.lock) {{
                s_d.c = (s_d.c || 0) + 1;
                sc.width = vs.offsetWidth; sc.height = vs.offsetHeight;
                sctx.clearRect(0, 0, sc.width, sc.height);

                const hC = {{x:(lm[23].x+lm[24].x)/2, y:(lm[23].y+lm[24].y)/2}};
                const sC = {{x:(lm[11].x+lm[12].x)/2, y:(lm[11].y+lm[12].y)/2}};
                const curSp = Math.abs(Math.atan2(hC.y - sC.y, hC.x - sC.x) * 180/Math.PI);

                if (s_d.c === 10) s_d.addr = {{s:sC, h:hC, ang:curSp}};
                if (s_d.addr) drawLine(sctx, sc, s_d.addr.s, s_d.addr.h, '#00f', 2); // 어드레스(청색)

                if (wR.y < lm[11].y) {{
                    s_d.topP = true;
                    if (!s_d.topL || curSp > s_d.topL.ang) s_d.topL = {{s:sC, h:hC, ang:curSp}};
                }}
                if (s_d.topL) drawLine(sctx, sc, s_d.topL.s, s_d.topL.h, '#f00', 2); // 탑(적색)

                if (s_d.topP && wR.y > lm[23].y - 0.02) {{
                    s_d.lock = true;
                    s_d.impL = {{s:sC, h:hC}}; // 임팩트(녹색)
                }}

                drawLine(sctx, sc, sC, hC, '#0f0', 3);
                if(s_d.impL) drawLine(sctx, sc, s_d.impL.s, s_d.impL.h, '#0f0', 4);

                let d = s_d.addr ? Math.abs(curSp - s_d.addr.ang) : 0;
                document.getElementById('s_sp').innerText = d.toFixed(1);
            }}
        }}

        async function loop(v) {{
            v.playbackRate = 0.2;
            while(!v.paused && !v.ended) {{
                await pose.send({{image: v}});
                await new Promise(r => setTimeout(r, 40));
            }}
        }}

        vf.onplay = () => {{ initEngine(); f_d = {{}}; loop(vf); }};
        vs.onplay = () => {{ initEngine(); s_d = {{}}; loop(vs); }};

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
    </script>
    """

f_file = st.file_uploader("Front Video", type=['mp4', 'mov'])
s_file = st.file_uploader("Side Video", type=['mp4', 'mov'])

if f_file and s_file:
    f_b = base64.b64encode(f_file.read()).decode()
    s_b = base64.b64encode(s_file.read()).decode()
    components.html(get_debugged_engine(f_b, s_b), height=1500)
