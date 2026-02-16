import streamlit as st
import base64
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="GDR AI Pro v102")
st.title("⛳ GDR AI Pro: Sway 교정 및 하드 래치 v102.0")

def get_calibrated_engine(f_v64, s_v64):
    return f"""
    <style>
        .v-box {{ background: #111; padding: 15px; border-radius: 12px; border: 1px solid #333; margin-bottom: 20px; }}
        video {{ width: 100%; border-radius: 10px; background: #000; }}
        .val-disp {{ margin-top:10px; color:#0f0; font-family:monospace; font-size:26px; font-weight:bold; background:rgba(0,0,0,0.5); padding:15px; border-radius:8px; border:1px solid #0f0; text-align:center; }}
        #log {{ font-size: 14px; color: #ff0; background: #222; padding: 10px; border-radius: 5px; margin-top: 10px; font-family: monospace; }}
    </style>

    <div id="log">상태: 분석 대기 중...</div>
    
    <div class="v-box">
        <h4 style="color:#0f0; margin:0;">FRONT VIEW</h4>
        <video id="vf" controls playsinline muted></video>
        <div class="val-disp">Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°</div>
    </div>

    <div class="v-box">
        <h4 style="color:#0f0; margin:0;">SIDE VIEW</h4>
        <video id="vs" controls playsinline muted></video>
        <div class="val-disp">Δ Spine: <span id="s_sp">0.0</span>° | Knee: <span id="s_kn">0.0</span>°</div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs'), log=document.getElementById('log');
        let pose = null;
        let f_d = {{}}, s_d = {{}};

        function init() {{
            if(pose) pose.close();
            pose = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
            pose.setOptions({{modelComplexity:0, smoothLandmarks:true, minDetectionConfidence:0.45}});
            pose.onResults(onResults);
        }}

        function onResults(r) {{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hL=lm[24], hR=lm[23], sL=lm[12], sR=lm[11], wL=lm[16], wR=lm[15];

            // 1. 정면 분석 (Sway 로직 강화)
            if (!vf.paused && !f_d.lock) {{
                f_d.c++;
                // 기준점을 첫 3프레임 내에 고정하여 백스윙 즉시 반영
                if (f_d.c < 4) f_d.stCX = (hL.x + hR.x) / 2;

                let sw = (( (hL.x + hR.x)/2 - f_d.stCX ) / 0.15) * 100;
                // 백스윙(오른쪽) 이동만 기록 (음수값 무시 및 감도 부스팅)
                if(sw > f_d.pkSw && sw < 25) f_d.pkSw = sw;
                document.getElementById('f_sw').innerText = f_d.pkSw.toFixed(1);

                let xf = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                if(xf > f_d.pkXF && xf < 68) f_d.pkXF = xf;
                document.getElementById('f_xf').innerText = (f_d.pkXF * 1.1).toFixed(1);

                // 하드 래치: 백스윙 탑 이후 손목이 다시 어깨 높이 아래로 내려오면 즉시 잠금
                if (wL.y < sL.y) f_d.top = true;
                if (f_d.top && wL.y > (sL.y + 0.05)) {{
                    f_d.lock = true;
                    log.innerText = "상태: 정면 임팩트 시점 고정 완료";
                }}
            }}

            // 2. 측면 분석 (Delta Spine 보정)
            if (!vs.paused && !s_d.lock) {{
                s_d.c++;
                const hC_y = (lm[23].y + lm[24].y)/2, hC_x = (lm[23].x + lm[24].x)/2;
                const sC_y = (lm[11].y + lm[12].y)/2, sC_x = (lm[11].x + lm[12].x)/2;
                const sp = Math.abs(Math.atan2(hC_y - sC_y, hC_x - sC_x) * 180/Math.PI);
                
                if(s_d.c < 5) s_d.initS = sp;
                else {{
                    let d = Math.abs(sp - s_d.initS);
                    if(d > s_d.pkSp && d < 18) s_d.pkSp = d;
                    document.getElementById('s_sp').innerText = s_d.pkSp.toFixed(1);

                    let kn = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI);
                    if(kn > s_d.pkKn) s_d.pkKn = kn;
                    document.getElementById('s_kn').innerText = s_d.pkKn.toFixed(1);

                    if (wR.y < sR.y) s_d.top = true;
                    if (s_d.top && wR.y > hR.y) s_d.lock = true;
                }}
            }}
        }

        async function stream(v) {{
            while(!v.paused && !v.ended) {{
                await pose.send({{image: v}});
                await new Promise(r => setTimeout(r, 45));
            }}
        }}

        vf.onplay = () => {{ 
            init(); f_d = {{ pkSw:0, pkXF:0, c:0, lock:false, stCX:0, top:false }};
            document.querySelectorAll('#f_sw, #f_xf').forEach(s => s.innerText = "0.0");
            stream(vf); 
        }};
        vs.onplay = () => {{ 
            if(!pose) init(); s_d = {{ pkSp:0, pkKn:0, c:0, lock:false, initS:0, top:false }};
            document.querySelectorAll('#s_sp, #s_kn').forEach(s => s.innerText = "0.0");
            stream(vs); 
        }};

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
    </script>
    """

f_f = st.file_uploader("정면 영상", type=['mp4', 'mov'])
s_f = st.file_uploader("측면 영상", type=['mp4', 'mov'])

if f_f and s_f:
    f_b = base64.b64encode(f_f.read()).decode()
    s_b = base64.b64encode(s_f.read()).decode()
    components.html(get_calibrated_engine(f_b, s_b), height=1400)
