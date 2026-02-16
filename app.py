import streamlit as st
import base64
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="GDR AI Pro v118")
st.title("⛳ GDR AI Pro: 척추각 오버레이 롤백 v118.0")

def get_rollback_engine(f_v64, s_v64):
    return f"""
    <style>
        .v-box {{ position: relative; background: #111; padding: 15px; border-radius: 12px; border: 1px solid #333; margin-bottom: 20px; }}
        video {{ width: 100%; border-radius: 10px; display: block; }}
        canvas {{ position: absolute; top: 15px; left: 15px; width: calc(100% - 30px); height: calc(100% - 100px); pointer-events: none; z-index: 5; }}
        .val-disp {{ margin-top:10px; color:#0f0; font-family:monospace; font-size:26px; font-weight:bold; background:rgba(0,0,0,0.5); padding:15px; border-radius:8px; border:1px solid #0f0; text-align:center; }}
    </style>

    <div class="v-box">
        <h4 style="color:#0f0; margin:0 0 10px 0;">FRONT VIEW</h4>
        <video id="vf" controls playsinline muted></video>
        <div class="val-disp">Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°</div>
    </div>

    <div class="v-box">
        <h4 style="color:#0f0; margin:0 0 10px 0;">SIDE VIEW: 3단 척추각 오버레이</h4>
        <video id="vs" controls playsinline muted></video>
        <canvas id="sc"></canvas>
        <div class="val-disp">Δ Spine: <span id="s_sp">0.0</span>° | Knee: <span id="s_kn">0.0</span>°</div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs');
        const sc=document.getElementById('sc'), ctx=sc.getContext('2d');
        let pose = null, f_d = {{}}, s_d = {{}};

        function init() {{
            if(pose) pose.close();
            pose = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
            pose.setOptions({{modelComplexity:1, smoothLandmarks:true, minDetectionConfidence:0.5}});
            pose.onResults(onResults);
        }}

        function drawSpine(s, h, color, width=2) {{
            ctx.beginPath();
            ctx.moveTo(s.x * sc.width, s.y * sc.height);
            ctx.lineTo(h.x * sc.width, h.y * sc.height);
            ctx.strokeStyle = color;
            ctx.lineWidth = width;
            ctx.stroke();
        }}

        function onResults(r) {{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hL=lm[24], hR=lm[23], sL=lm[12], sR=lm[11], wL=lm[16], wR=lm[15];

            // 1. 정면 분석 로직
            if (!vf.paused && !f_d.lock) {{
                f_d.c++;
                let curCX = (hL.x + hR.x) / 2;
                if (f_d.c <= 5) f_d.stCX = curCX;
                else {{
                    let sw = ((f_d.stCX - curCX) / 0.1) * 100;
                    if(sw > f_d.pkSw && sw < 25) f_d.pkSw = sw;
                    document.getElementById('f_sw').innerText = Math.max(0, f_d.pkSw).toFixed(1);

                    let xf = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                    if(xf > f_d.pkXF && xf < 68) f_d.pkXF = xf;
                    document.getElementById('f_xf').innerText = (f_d.pkXF * 1.1).toFixed(1);

                    if (wL.y < sL.y) f_d.top = true;
                    if (f_d.top && wL.y > hL.y - 0.05) f_d.lock = true;
                }}
            }}

            // 2. 측면 분석 (롤백된 3단 오버레이 로직)
            if (!vs.paused && !s_d.lock) {{
                s_d.c++;
                sc.width = vs.clientWidth; sc.height = vs.clientHeight;
                const hC = {{x:(lm[23].x+lm[24].x)/2, y:(lm[23].y+lm[24].y)/2}};
                const sC = {{x:(lm[11].x+lm[12].x)/2, y:(lm[11].y+lm[12].y)/2}};
                const curSp = Math.abs(Math.atan2(hC.y - sC.y, hC.x - sC.x) * 180/Math.PI);

                ctx.clearRect(0, 0, sc.width, sc.height);

                // 어드레스 기준선 (청색)
                if (s_d.c === 10) s_d.addr = {{s:sC, h:hC, ang:curSp}};
                if (s_d.addr) drawSpine(s_d.addr.s, s_d.addr.h, '#00f', 2);

                // 백스윙 탑 선 (적색)
                if (wR.y < lm[11].y) {{
                    s_d.topP = true;
                    if (!s_d.topL || curSp > s_d.topL.ang) s_d.topL = {{s:sC, h:hC, ang:curSp}};
                }}
                if (s_d.topL) drawSpine(s_d.topL.s, s_d.topL.h, '#f00', 2);

                // 임팩트 판정 및 선 (녹색)
                if (s_d.topP && wR.y > lm[23].y - 0.02) {{
                    s_d.lock = true;
                    s_d.impL = {{s:sC, h:hC}};
                }}

                drawSpine(sC, hC, '#0f0', 3); // 실시간 척추선
                if(s_d.impL) drawSpine(s_d.impL.s, s_d.impL.h, '#0f0', 4);
                
                let diff = s_d.addr ? Math.abs(curSp - s_d.addr.ang) : 0;
                if(s_d.topP) {{
                    let d_down = Math.abs(curSp - s_d.topL.ang);
                    if(d_down > s_d.pkSp) s_d.pkSp = d_down;
                }} else if(diff > s_d.pkSp) s_d.pkSp = diff;

                document.getElementById('s_sp').innerText = s_d.pkSp.toFixed(1);
            }}
        }}

        async function loop(v) {{
            v.playbackRate = 0.2; // 슬로우 재생 유지
            while(!v.paused && !v.ended) {{
                await pose.send({{image: v}});
                await new Promise(r => setTimeout(r, 45));
            }}
        }}

        vf.onplay = () => {{ init(); f_d = {{ c:0, lock:false, stCX:0, top:false }}; loop(vf); }};
        vs.onplay = () => {{ init(); s_d = {{ c:0, lock:false, addr:null, topL:null, impL:null, topP:false, pkSp:0 }}; loop(vs); }};
    </script>
    """

f_file = st.file_uploader("Front Video", type=['mp4', 'mov'])
s_file = st.file_uploader("Side Video", type=['mp4', 'mov'])

if f_file and s_file:
    f_b = base64.b64encode(f_file.read()).decode()
    s_b = base64.b64encode(s_file.read()).decode()
    components.html(get_rollback_engine(f_b, s_b), height=1500)
