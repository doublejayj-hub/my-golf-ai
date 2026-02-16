import streamlit as st
import base64
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="GDR AI Pro v112")
st.title("⛳ GDR AI Pro: 골퍼 기준 좌표계 완전 교정 v112.0")

def get_final_alignment_engine(f_v64, s_v64):
    return f"""
    <style>
        .v-box {{ position: relative; background: #000; padding: 0; border-radius: 12px; border: 1px solid #333; margin-bottom: 25px; overflow: hidden; }}
        video {{ width: 100%; display: block; z-index: 1; }}
        canvas {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 2; }}
        .val-disp {{ margin-top:10px; color:#0f0; font-family:monospace; font-size:26px; font-weight:bold; background:rgba(0,0,0,0.8); padding:15px; border-radius:8px; border:1px solid #0f0; text-align:center; }}
    </style>

    <div class="v-box">
        <h4 style="color:#0f0; margin:10px;">FRONT: 골퍼 기준 왼발(타겟방향) 벽 가이드</h4>
        <video id="vf" controls playsinline muted></video>
        <canvas id="front_canvas"></canvas>
        <div class="val-disp">Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°</div>
    </div>

    <div class="v-box">
        <h4 style="color:#0f0; margin:10px;">SIDE: 엉덩이 최후방 Butt-Line (Early Extension 방지)</h4>
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

        function drawDashedLine(ctx, c, x, color) {{
            ctx.beginPath();
            ctx.setLineDash([10, 5]);
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
            const hL=lm[24], hR=lm[23], sL=lm[12], sR=lm[11], wL=lm[16], aL=lm[28], aR=lm[27];

            // 1. 정면 분석: 골퍼 기준 왼발(화면상 우측)
            if (!vf.paused && !f_d.lock) {{
                f_d.c++;
                fc.width = vf.offsetWidth; fc.height = vf.offsetHeight;
                fctx.clearRect(0, 0, fc.width, fc.height);
                
                // 골퍼의 왼발(타겟 방향)은 화면상 우측 좌표인 lm[28]입니다.
                if (f_d.c <= 10) f_d.wallX = aL.x; 
                if (f_d.wallX) drawDashedLine(fctx, fc, f_d.wallX, '#00ff00');

                if (f_d.c === 1) f_d.stCX = (hL.x + hR.x) / 2;
                let sw = ((f_d.stCX - (hL.x + hR.x)/2) / 0.1) * 100;
                document.getElementById('f_sw').innerText = Math.max(0, sw).toFixed(1);

                let xf = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                document.getElementById('f_xf').innerText = (xf * 1.1).toFixed(1);
            }}

            // 2. 측면 분석: 엉덩이 최후방 (골퍼 뒤쪽)
            if (!vs.paused && !s_d.lock) {{
                s_d.c++;
                sc.width = vs.offsetWidth; sc.height = vs.offsetHeight;
                sctx.clearRect(0, 0, sc.width, sc.height);
                
                // 측면에서 엉덩이 뒷라인은 x 좌표의 '최댓값'을 가진 지점입니다.
                let currentButt = Math.max(lm[23].x, lm[24].x);
                if (s_d.c <= 10) s_d.buttX = currentButt;
                
                if (s_d.buttX) drawDashedLine(sctx, sc, s_d.buttX, '#0000ff');

                let kn = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI);
                document.getElementById('s_kn').innerText = kn.toFixed(1);
            }}
        }}

        async function loop(v) {{
            v.playbackRate = 0.2;
            while(!v.paused && !v.ended) {{
                await pose.send({{image: v}});
                await new Promise(r => setTimeout(r, 40));
            }}
        }}

        vf.onplay = () => {{ initEngine(); f_d = {{ c:0, lock:false, stCX:0 }}; loop(vf); }};
        vs.onplay = () => {{ initEngine(); s_d = {{ c:0, lock:false, buttX:0 }}; loop(vs); }};

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
    </script>
    """

f_file = st.file_uploader("Front Video (정면)", type=['mp4', 'mov'])
s_file = st.file_uploader("Side Video (측면)", type=['mp4', 'mov'])

if f_file and s_file:
    f_b = base64.b64encode(f_file.read()).decode()
    s_b = base64.b64encode(s_file.read()).decode()
    components.html(get_final_alignment_engine(f_b, s_b), height=1500)
