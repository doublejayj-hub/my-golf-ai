import streamlit as st
import base64
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="GDR AI Pro v111")
st.title("⛳ GDR AI Pro: 골퍼 기준 축 고정 및 엉덩이 라인 v111.0")

def get_pro_alignment_engine(f_v64, s_v64):
    return f"""
    <style>
        .v-box {{ position: relative; background: #000; padding: 0; border-radius: 12px; border: 1px solid #333; margin-bottom: 25px; overflow: hidden; }}
        video {{ width: 100%; display: block; z-index: 1; }}
        canvas {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 2; }}
        .val-disp {{ margin-top:10px; color:#0f0; font-family:monospace; font-size:26px; font-weight:bold; background:rgba(0,0,0,0.8); padding:15px; border-radius:8px; border:1px solid #0f0; text-align:center; }}
    </style>

    <div class="v-box">
        <h4 style="color:#0f0; margin:10px;">FRONT: 골퍼 기준 왼발(타겟) 벽 고정</h4>
        <video id="vf" controls playsinline muted></video>
        <canvas id="front_canvas"></canvas>
        <div class="val-disp">Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°</div>
    </div>

    <div class="v-box">
        <h4 style="color:#0f0; margin:10px;">SIDE: 엉덩이 최후방 라인 (Butt-Line)</h4>
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

        function drawVLine(ctx, c, x, color, width=3) {{
            ctx.beginPath();
            ctx.setLineDash([8, 4]);
            ctx.moveTo(x * c.width, 0);
            ctx.lineTo(x * c.width, c.height);
            ctx.strokeStyle = color;
            ctx.lineWidth = width;
            ctx.stroke();
            ctx.setLineDash([]);
        }}

        function onResults(r) {{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hL=lm[24], hR=lm[23], sL=lm[12], sR=lm[11], wL=lm[16], aL=lm[28], aR=lm[27];

            // 1. 정면 분석: 골퍼 기준 왼발(Target Side) 벽 설정
            if (!vf.paused && !f_d.lock) {{
                f_d.c++;
                fc.width = vf.offsetWidth; fc.height = vf.offsetHeight;
                fctx.clearRect(0, 0, fc.width, fc.height);
                
                // 골퍼 기준 왼발(일반적으로 화면상 오른쪽) 바깥쪽 복사뼈 좌표를 벽으로 설정
                if (f_d.c <= 8) f_d.wallX = aL.x; 
                if (f_d.wallX) drawVLine(fctx, fc, f_d.wallX, '#00ff00'); // 벽은 녹색 가이드로 표시

                if (f_d.c === 1) f_d.stCX = (hL.x + hR.x) / 2;
                let sw = ((f_d.stCX - (hL.x + hR.x)/2) / 0.1) * 100;
                if(sw > f_d.pkSw && sw < 25) f_d.pkSw = sw;
                document.getElementById('f_sw').innerText = Math.max(0, f_d.pkSw).toFixed(1);

                let xf = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                if(xf > f_d.pkXF && xf < 68) f_d.pkXF = xf;
                document.getElementById('f_xf').innerText = (f_d.pkXF * 1.1).toFixed(1);

                if (wL.y < sL.y) f_d.top = true;
                if (f_d.top && wL.y > hL.y - 0.05) f_d.lock = true;
            }}

            // 2. 측면 분석: 엉덩이 최후방 라인 (Butt-Line)
            if (!vs.paused && !s_d.lock) {{
                s_d.c++;
                sc.width = vs.offsetWidth; sc.height = vs.offsetHeight;
                sctx.clearRect(0, 0, sc.width, sc.height);
                
                // 엉덩이 왼쪽/오른쪽 포인트 중 더 뒤에 있는(x값이 큰) 좌표를 기준으로 선 설정
                let curButtX = Math.max(lm[23].x, lm[24].x);
                if (s_d.c <= 10) s_d.buttX = curButtX;
                
                if (s_d.buttX) drawVLine(sctx, sc, s_d.buttX, '#0000ff'); // Butt-line은 청색 가이드

                let kn = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI);
                if(kn > s_d.pkKn) s_d.pkKn = kn;
                document.getElementById('s_kn').innerText = s_d.pkKn.toFixed(1);
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
        vs.onplay = () => {{ initEngine(); s_d = {{ pkSp:0, pkKn:0, c:0, lock:false, buttX:0 }}; loop(vs); }};

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
    </script>
    """

f_file = st.file_uploader("정면 영상", type=['mp4', 'mov'])
s_file = st.file_uploader("측면 영상", type=['mp4', 'mov'])

if f_file and s_file:
    f_b = base64.b64encode(f_file.read()).decode()
    s_b = base64.b64encode(s_file.read()).decode()
    components.html(get_pro_alignment_engine(f_b, s_b), height=1500)
