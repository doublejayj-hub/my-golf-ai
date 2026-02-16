import streamlit as st
import base64
import streamlit.components.v1 as components

# [1] 페이지 설정 및 제목
st.set_page_config(layout="wide", page_title="GDR AI Pro v103")
st.title("⛳ GDR AI Pro: 구문 수정 및 수치 정합성 v103.0")

# [2] 고정밀 분석 엔진 (f-string 중괄호 이스케이프 적용)
def get_fixed_engine(f_v64, s_v64):
    # 파이썬 f-string 내에서 JS 중괄호는 {{ }} 로 작성해야 함
    return f"""
    <style>
        .v-box {{ background: #111; padding: 15px; border-radius: 12px; border: 1px solid #333; margin-bottom: 20px; }}
        video {{ width: 100%; border-radius: 10px; background: #000; }}
        .val-disp {{ margin-top:10px; color:#0f0; font-family:monospace; font-size:26px; font-weight:bold; background:rgba(0,0,0,0.5); padding:15px; border-radius:8px; border:1px solid #0f0; text-align:center; }}
        #log {{ font-size: 14px; color: #ff0; background: #222; padding: 10px; border-radius: 5px; margin-top: 10px; font-family: monospace; }}
    </style>

    <div id="log">상태: 시스템 정상 가동 중...</div>
    
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

            // 1. 정면 분석 (Sway 백스윙 즉시 반영)
            if (!vf.paused && !f_d.lock) {{
                f_d.c++;
                if (f_d.c < 4) f_d.stCX = (hL.x + hR.x) / 2;

                let sw = (( (hL.x + hR.x)/2 - f_d.stCX ) / 0.15) * 100;
                if(sw > f_d.pkSw && sw < 25) f_d.pkSw = sw;
                document.getElementById('f_sw').innerText = f_d.pkSw.toFixed(1);

                let xf = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                if(xf > f_d.pkXF && xf < 68) f_d.pkXF = xf;
                document.getElementById('f_xf').innerText = (f_d.pkXF * 1.1).toFixed(1);

                if (wL.y < sL.y) f_d.top = true;
                if (f_d.top && wL.y > (sL.y + 0.05)) f_d.lock = true;
            }}

            // 2. 측면 분석 (Delta Spine 보정)
            if (!vs.paused && !s_d.lock) {{
                s_d.c++;
                const hCy = (lm[23].y + lm[24].y)/2, hCx = (lm[23].x + lm[24].x)/2;
                const sCy = (lm[11].y + lm[12].y)/2, sCx = (lm[11].x + lm[12].x)/2;
                const sp = Math.abs(Math.atan2(hCy - sCy, hCx - sCx) * 180/Math.PI);
                
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
        }}

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

# [3] 파일 업로드 및 분석 실행
f_file = st.file_uploader("Front Video (정면)", type=['mp4', 'mov'])
s_file = st.file_uploader("Side Video (측면)", type=['mp4', 'mov'])

if f_file and s_file:
    f_b64 = base64.b64encode(f_file.read()).decode()
    s_b64 = base64.b64encode(s_file.read()).decode()
    components.html(get_fixed_engine(f_b64, s_b64), height=1400)
