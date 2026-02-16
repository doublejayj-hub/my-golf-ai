import streamlit as st
import base64
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="GDR AI Pro v110")
st.title("⛳ GDR AI Pro: 프로급 스윙 가이드 오버레이 v110.0")

def get_pro_visual_engine(f_v64, s_v64):
    return f"""
    <style>
        .v-box {{ position: relative; background: #000; padding: 0; border-radius: 12px; border: 1px solid #333; margin-bottom: 25px; overflow: hidden; }}
        video {{ width: 100%; display: block; z-index: 1; }}
        canvas {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 2; }}
        .val-disp {{ margin-top:10px; color:#0f0; font-family:monospace; font-size:26px; font-weight:bold; background:rgba(0,0,0,0.8); padding:15px; border-radius:8px; border:1px solid #0f0; text-align:center; }}
    </style>

    <div class="v-box">
        <h4 style="color:#0f0; margin:10px;">FRONT: 왼발 벽(Wall) 가이드</h4>
        <video id="vf" controls playsinline muted></video>
        <canvas id="front_canvas"></canvas>
        <div class="val-disp">Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°</div>
    </div>

    <div class="v-box">
        <h4 style="color:#0f0; margin:10px;">SIDE: 엉덩이 라인(Butt-Line) 가이드</h4>
        <video id="vs" controls playsinline muted></video>
        <canvas id="side_canvas"></canvas>
        <div class="val-disp">Δ Spine: <span id="s_sp">0.0</span>° | Knee: <span id="s_kn">0.0</span>°</div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs');
        const fc=document.getElementById('front_canvas'), fctx=fc.getContext('2d');
        const sc=document.getElementById('side_canvas'), sctx=sc.getContext('2d');
        let pose = null, f_d = {{}}, s_d = {{}};

        function initEngine() {{
            if(pose) pose.close();
            pose = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
            pose.setOptions({{modelComplexity:1, smoothLandmarks:true, minDetectionConfidence:0.5}});
            pose.onResults(onResults);
        }}

        function drawVLine(ctx, c, x, color, width=2) {{
            ctx.beginPath();
            ctx.moveTo(x * c.width, 0);
            ctx.lineTo(x * c.width, c.height);
            ctx.strokeStyle = color;
            ctx.setLineDash([5, 5]); // 점선 처리
            ctx.lineWidth = width;
            ctx.stroke();
            ctx.setLineDash([]); // 실선 복구
        }}

        function onResults(r) {{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hL=lm[24], hR=lm[23], sL=lm[12], sR=lm[11], wL=lm[16], wR=lm[15], aL=lm[28];

            // 1. 정면 분석 및 왼발 벽 오버레이
            if (!vf.paused && !f_d.lock) {{
                f_d.c++;
                fc.width = vf.offsetWidth; fc.height = vf.offsetHeight;
                fctx.clearRect(0, 0, fc.width, fc.height);
                
                if (f_d.c <= 5) {{
                    f_d.stCX = (hL.x + hR.x) / 2;
                    f_d.wallX = aL.x; // 왼발 바깥쪽 좌표 저장
                }}
                
                // 가상 벽(Wall) 오버레이 (청색 점선)
                if(f_d.wallX) drawVLine(fctx, fc, f_d.wallX, '#00f', 3);

                let sw = ((f_d.stCX - (hL.x + hR.x)/2) / 0.1) * 100;
                if(sw > f_d.pkSw && sw < 25) f_d.pkSw = sw;
                document.getElementById('f_sw').innerText = Math.max(0, f_d.pkSw).toFixed(1);

                let xf = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                if(xf > f_d.pkXF && xf < 65) f_d.pkXF = xf;
                document.getElementById('f_xf').innerText = (f_d.pkXF * 1.1).toFixed(1);

                if (wL.y < sL.y) f_d.top = true;
                if (f_d.top && wL.y > hL.y - 0.05) f_d.lock = true;
            }}

            // 2. 측면 분석 및 엉덩이 라인 오버레이
            if (!vs.paused && !s_d.lock) {{
                s_d.c++;
                sc.width = vs.offsetWidth; sc.height = vs.offsetHeight;
                sctx.clearRect(0, 0, sc.width, sc.height);
                
                const hC = {{x:(lm[23].x+lm[24].x)/2, y:(lm[23].y+lm[24].y)/2}};
                if (s_d.c <= 10) s_d.buttX = Math.max(lm[23].x, lm[24].x); // 엉덩이 가장 뒷부분 저장

                // 엉덩이 라인(Butt-Line) 오버레이 (주황색 점선)
                if(s_d.buttX) drawVLine(sctx, sc, s_d.buttX, '#ff8c00', 3);

                let kn = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI);
                if(kn > s_d.pkKn) s_d.pkKn = kn;
                document.getElementById('s_kn').innerText = s_d.pkKn.toFixed(1);
            }}
        }}

        async function stream(v) {{
            v.playbackRate = 0.2;
            while(!v.paused && !v.ended) {{
                await pose.send({{image: v}});
                await new Promise(r => setTimeout(r, 40));
            }}
        }}

        vf.onplay = () => {{ initEngine(); f_d = {{ pkSw:0, pkXF:0, c:0, lock:false, stCX:0, top:false }}; stream(vf); }};
        vs.onplay = () => {{ initEngine(); s_d = {{ pkSp:0, pkKn:0, c:0, lock:false, buttX:0 }}; stream(vs); }};

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
    </script>
    """

f_f = st.file_uploader("정면 영상", type=['mp4', 'mov'])
s_f = st.file_uploader("측면 영상", type=['mp4', 'mov'])

if f_f and s_f:
    f_b = base64.b64encode(f_f.read()).decode()
    s_b = base64.b64encode(s_f.read()).decode()
    components.html(get_pro_visual_engine(f_b, s_b), height=1500)
