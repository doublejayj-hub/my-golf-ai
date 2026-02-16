import streamlit as st
import base64
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="GDR AI Pro v120")
st.title("⛳ GDR AI Pro: 골든 버전 기반 가이드 추가 v120.0")

def get_golden_plus_engine(f_v64, s_v64):
    return f"""
    <style>
        .v-box {{ position: relative; background: #000; padding: 0; border-radius: 12px; border: 1px solid #333; margin-bottom: 25px; overflow: hidden; }}
        video {{ width: 100%; display: block; z-index: 1; }}
        canvas {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 2; }}
        .val-disp {{ margin-top:10px; color:#0f0; font-family:monospace; font-size:26px; font-weight:bold; background:rgba(0,0,0,0.8); padding:15px; border-radius:8px; border:1px solid #0f0; text-align:center; }}
        #log {{ font-size: 14px; color: #ff0; background: #222; padding: 10px; text-align:center; margin-bottom: 10px; border-radius: 5px; }}
    </style>

    <div id="log">골든 버전 엔진 가동 준비 완료.</div>
    
    <div class="v-box">
        <video id="vf" controls playsinline muted></video>
        <canvas id="front_canvas"></canvas>
        <div class="val-disp">Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°</div>
    </div>

    <div class="v-box">
        <video id="vs" controls playsinline muted></video>
        <canvas id="side_canvas"></canvas>
        <div class="val-disp">Δ Spine: <span id="s_sp">0.0</span>° | Knee: <span id="s_kn">0.0</span>°</div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs');
        const sc=document.getElementById('side_canvas'), sctx=sc.getContext('2d');
        const fc=document.getElementById('front_canvas'), fctx=fc.getContext('2d');
        let pose = null, f_d = {{}}, s_d = {{}};

        function initEngine() {{
            if(pose) {{ pose.close(); }}
            pose = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
            pose.setOptions({{modelComplexity:1, smoothLandmarks:true, minDetectionConfidence:0.5}});
            pose.onResults(onResults);
        }}

        function drawLine(ctx, c, p1, p2, color, width=2) {{
            ctx.beginPath();
            ctx.moveTo(p1.x * c.width, p1.y * c.height);
            ctx.lineTo(p2.x * c.width, p2.y * c.height);
            ctx.strokeStyle = color;
            ctx.lineWidth = width;
            ctx.stroke();
        }}

        // 세로 점선 그리기 함수 추가
        function drawVWall(ctx, c, x, color) {{
            ctx.beginPath();
            ctx.setLineDash([10, 10]);
            ctx.moveTo(x * c.width, 0);
            ctx.lineTo(x * c.width, c.height);
            ctx.strokeStyle = color;
            ctx.lineWidth = 4;
            ctx.stroke();
            ctx.setLineDash([]);
        }}

        function onResults(r) {{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hL=lm[24], hR=lm[23], sL=lm[12], sR=lm[11], wL=lm[16], wR=lm[15];

            // 1. [정면] 골든 버전 로직 + 왼발 벽 추가
            if (!vf.paused && !f_d.lock) {{
                f_d.c = (f_d.c || 0) + 1;
                fc.width = vf.offsetWidth; fc.height = vf.offsetHeight;
                fctx.clearRect(0, 0, fc.width, fc.height);

                let curCX = (hL.x + hR.x) / 2;
                if (f_d.c <= 10) {{
                    f_d.stCX = curCX;
                    f_d.wallX = lm[28].x; // 골퍼 기준 왼발(화면 우측) 좌표 고정
                }}
                
                if (f_d.wallX) drawVWall(fctx, fc, f_d.wallX, '#00ff00'); // 녹색 벽 가이드

                let sw = ((f_d.stCX - curCX) / 0.1) * 100;
                if(sw > (f_d.pkSw || 0) && sw < 25) f_d.pkSw = sw;
                document.getElementById('f_sw').innerText = Math.max(0, f_d.pkSw || 0).toFixed(1);

                let xf = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                if(xf > (f_d.pkXF || 0) && xf < 68) f_d.pkXF = xf;
                document.getElementById('f_xf').innerText = ((f_d.pkXF || 0) * 1.1).toFixed(1);

                if (wL.y < sL.y) f_d.top = true;
                if (f_d.top && wL.y > hL.y - 0.05) f_d.lock = true;
            }}

            // 2. [측면] 골든 버전 로직 + 엉덩이 선 추가
            if (!vs.paused && !s_d.lock) {{
                s_d.c = (s_d.c || 0) + 1;
                sc.width = vs.offsetWidth; sc.height = vs.offsetHeight;
                const hC = {{x:(lm[23].x+lm[24].x)/2, y:(lm[23].y+lm[24].y)/2}};
                const sC = {{x:(lm[11].x+lm[12].x)/2, y:(lm[11].y+lm[12].y)/2}};
                const curSp = Math.abs(Math.atan2(hC.y - sC.y, hC.x - sC.x) * 180/Math.PI);

                sctx.clearRect(0, 0, sc.width, sc.height);
                
                // 엉덩이 최후방(x값 최대치) 좌표 고정
                if (s_d.c <= 15) s_d.buttX = Math.max(lm[23].x, lm[24].x);
                if (s_d.buttX) drawVWall(sctx, sc, s_d.buttX, '#0000ff'); // 청색 엉덩이 가이드

                if (s_d.c === 10) s_d.addr = {{s:sC, h:hC, ang:curSp}};
                if (s_d.addr) drawLine(sctx, sc, s_d.addr.s, s_d.addr.h, '#00f', 2);

                if (wR.y < lm[11].y) {{
                    s_d.topP = true;
                    if (!s_d.topL || curSp > s_d.topL.ang) s_d.topL = {{s:sC, h:hC, ang:curSp}};
                }}
                if (s_d.topL) drawLine(sctx, sc, s_d.topL.s, s_d.topL.h, '#f00', 2);

                if (s_d.topP && wR.y > lm[23].y - 0.02) {{
                    s_d.lock = true;
                    s_d.impL = {{s:sC, h:hC}};
                }}

                drawLine(sctx, sc, sC, hC, '#0f0', 3);
                if(s_d.impL) drawLine(sctx, sc, s_d.impL.s, s_d.impL.h, '#0f0', 4);
                
                let d = s_d.addr ? Math.abs(curSp - s_d.addr.ang) : 0;
                if(s_d.topP) {{
                    let d_down = Math.abs(curSp - (s_d.topL ? s_d.topL.ang : curSp));
                    if(d_down > (s_d.pkSp || 0)) s_d.pkSp = d_down;
                }} else if(d > (s_d.pkSp || 0)) s_d.pkSp = d;

                document.getElementById('s_sp').innerText = (s_d.pkSp || 0).toFixed(1);
                let kn = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI);
                if(kn > (s_d.pkKn || 0)) s_d.pkKn = kn;
                document.getElementById('s_kn').innerText = (s_d.pkKn || 0).toFixed(1);
            }}
        }}

        async function loop(v) {{
            v.playbackRate = 0.2;
            while(!v.paused && !v.ended) {{
                await pose.send({{image: v}});
                await new Promise(r => setTimeout(r, 40));
            }}
        }}

        vf.onplay = () => {{ initEngine(); f_d = {{ pkSw:0, pkXF:0, c:0, lock:false, stCX:0, top:false }}; loop(vf); }};
        vs.onplay = () => {{ initEngine(); s_d = {{ pkSp:0, pkKn:0, c:0, lock:false, addr:null, topL:null, impL:null, topP:false }}; loop(vs); }};

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
    </script>
    """

f_file = st.file_uploader("Front Video (정면)", type=['mp4', 'mov'])
s_file = st.file_uploader("Side Video (측면)", type=['mp4', 'mov'])

if f_file and s_file:
    f_b = base64.b64encode(f_file.read()).decode()
    s_b = base64.b64encode(s_file.read()).decode()
    components.html(get_golden_plus_engine(f_b, s_b), height=1500)
