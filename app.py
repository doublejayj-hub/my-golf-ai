import streamlit as st
import base64
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="GDR AI Pro v113")
st.title("⛳ GDR AI Pro: 골퍼 기준 좌표계 물리 매핑 v113.0")

def get_final_fix_engine(f_v64, s_v64):
    return f"""
    <style>
        .v-box {{ position: relative; background: #000; border-radius: 12px; border: 1px solid #333; margin-bottom: 25px; overflow: hidden; }}
        video {{ width: 100%; display: block; z-index: 1; }}
        canvas {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 2; }}
        .val-disp {{ margin-top:10px; color:#0f0; font-family:monospace; font-size:26px; font-weight:bold; background:rgba(0,0,0,0.8); padding:15px; border-radius:8px; border:1px solid #0f0; text-align:center; }}
    </style>

    <div class="v-box">
        <h4 style="color:#0f0; margin:10px;">FRONT: 골퍼 기준 왼발(타겟) 벽 가이드</h4>
        <video id="vf" controls playsinline muted></video>
        <canvas id="fc"></canvas>
        <div class="val-disp">Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°</div>
    </div>

    <div class="v-box">
        <h4 style="color:#0f0; margin:10px;">SIDE: 엉덩이 최후방 Butt-Line</h4>
        <video id="vs" controls playsinline muted></video>
        <canvas id="sc"></canvas>
        <div class="val-disp">Δ Spine: <span id="s_sp">0.0</span>° | Knee: <span id="s_kn">0.0</span>°</div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs');
        const fc=document.getElementById('fc'), fctx=fc.getContext('2d');
        const sc=document.getElementById('sc'), sctx=sc.getContext('2d');
        let pose = null, f_s = {{}}, s_s = {{}};

        function initEngine() {{
            if(pose) pose.close();
            pose = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
            pose.setOptions({{modelComplexity:1, smoothLandmarks:true, minDetectionConfidence:0.5}});
            pose.onResults(onResults);
        }}

        function drawGuideline(ctx, canv, x, color) {{
            ctx.beginPath();
            ctx.setLineDash([10, 5]);
            ctx.moveTo(x * canv.width, 0);
            ctx.lineTo(x * canv.width, canv.height);
            ctx.strokeStyle = color;
            ctx.lineWidth = 4;
            ctx.stroke();
            ctx.setLineDash([]);
        }}

        function onResults(r) {{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            
            // 1. 정면 분석: 골퍼의 왼발(Target Side)은 화면 우측(lm[28])
            if (!vf.paused && !f_s.lock) {{
                f_s.c++;
                fc.width = vf.offsetWidth; fc.height = vf.offsetHeight;
                fctx.clearRect(0, 0, fc.width, fc.height);
                
                // 골퍼의 왼발(화면 우측) 복사뼈 좌표를 벽으로 고정
                if (f_s.c <= 15) f_s.wallX = lm[28].x; 
                if (f_s.wallX) drawGuideline(fctx, fc, f_s.wallX, '#00ff00');

                if (f_s.c === 1) f_s.startH = (lm[24].x + lm[23].x) / 2;
                let sway = ((f_s.startH - (lm[24].x + lm[23].x)/2) / 0.1) * 100;
                document.getElementById('f_sw').innerText = Math.max(0, sway).toFixed(1);
            }}

            // 2. 측면 분석: 엉덩이 최후방은 화면상 x값이 가장 큰 지점
            if (!vs.paused && !s_s.lock) {{
                s_s.c++;
                sc.width = vs.offsetWidth; sc.height = vs.offsetHeight;
                sctx.clearRect(0, 0, sc.width, sc.height);
                
                // 엉덩이(23, 24번) 중 등 뒤쪽(화면 우측 끝) 좌표를 라인으로 고정
                let currentButtEdge = Math.max(lm[23].x, lm[24].x);
                if (s_s.c <= 15) s_s.buttX = currentButtEdge;
                
                if (s_s.buttX) drawGuideline(sctx, sc, s_s.buttX, '#0000ff');
            }}
        }}

        async function loop(v) {{
            v.playbackRate = 0.2;
            while(!v.paused && !v.ended) {{
                await pose.send({{image: v}});
                await new Promise(r => setTimeout(r, 40));
            }}
        }}

        vf.onplay = () => {{ initEngine(); f_s = {{ c:0, lock:false, startH:0 }}; loop(vf); }};
        vs.onplay = () => {{ initEngine(); s_s = {{ c:0, lock:false, buttX:0 }}; loop(vs); }};

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
    </script>
    """

f_file = st.file_uploader("Front Video (정면)", type=['mp4', 'mov'])
s_file = st.file_uploader("Side Video (측면)", type=['mp4', 'mov'])

if f_file and s_file:
    f_b = base64.b64encode(f_file.read()).decode()
    s_b = base64.b64encode(s_file.read()).decode()
    components.html(get_final_fix_engine(f_b, s_b), height=1500)
