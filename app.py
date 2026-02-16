import streamlit as st
import base64
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="GDR AI Pro v101")
st.title("⛳ GDR AI Pro: 엔진 핫 리로드 및 프레임 동기화 v101.0")

def get_hot_reload_engine(f_v64, s_v64):
    return f"""
    <style>
        .v-box {{ background: #111; padding: 15px; border-radius: 12px; border: 1px solid #333; margin-bottom: 20px; }}
        video {{ width: 100%; border-radius: 10px; background: #000; }}
        .val-disp {{ margin-top:10px; color:#0f0; font-family:monospace; font-size:26px; font-weight:bold; background:rgba(0,0,0,0.5); padding:15px; border-radius:8px; border:1px solid #0f0; text-align:center; }}
        #log {{ font-size: 14px; color: #ff0; background: #222; padding: 10px; border-radius: 5px; margin-top: 10px; font-family: monospace; min-height: 40px; border: 1px dashed #555; }}
    </style>

    <div id="log">상태: 엔진 대기 중...</div>
    
    <div class="v-box">
        <video id="vf" controls playsinline muted></video>
        <div class="val-disp">Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°</div>
    </div>

    <div class="v-box">
        <video id="vs" controls playsinline muted></video>
        <div class="val-disp">Δ Spine: <span id="s_sp">0.0</span>° | Knee: <span id="s_kn">0.0</span>°</div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs'), log=document.getElementById('log');
        let pose = null;
        let f_data = {{}}, s_data = {{}};

        // [핵심] 엔진 인스턴스 신규 생성 함수
        function initEngine() {{
            if(pose) pose.close(); 
            pose = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
            pose.setOptions({{modelComplexity:0, smoothLandmarks:true, minDetectionConfidence:0.45}});
            pose.onResults(onResults);
            log.innerText = "상태: 엔진 신규 부팅 완료";
        }}

        function onResults(r) {{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hL=lm[24], hR=lm[23], sL=lm[12], sR=lm[11], wL=lm[16], wR=lm[15];

            // 1. 정면 분석 (재생 중이고 락이 아닐 때)
            if (!vf.paused && !f_data.lock) {{
                if (f_data.stCX === 0) f_data.stCX = (hL.x + hR.x) / 2;
                f_data.c++;

                if (wL.y < sL.y) f_data.top = true; 
                if (f_data.top && wL.y > hL.y) f_data.lock = true;

                if (!f_data.lock) {{
                    let sw = (((hL.x + hR.x)/2 - f_data.stCX) / 0.2) * 140;
                    if(sw > f_data.pkSw && sw < 25) f_data.pkSw = sw;
                    document.getElementById('f_sw').innerText = Math.abs(f_data.pkSw).toFixed(1);

                    let xf = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                    if(xf > f_data.pkXF && xf < 65) f_data.pkXF = xf;
                    document.getElementById('f_xf').innerText = (f_data.pkXF * 1.1).toFixed(1);
                }}
            }}

            // 2. 측면 분석
            if (!vs.paused && !s_data.lock) {{
                s_data.c++;
                const hC = (lm[23].y + lm[24].y)/2, sC = (lm[11].y + lm[12].y)/2;
                const sp = Math.abs(Math.atan2(hC-sC, (lm[23].x+lm[24].x)/2 - (lm[11].x+lm[12].x)/2) * 180/Math.PI);
                
                if(s_data.c < 10) s_data.initS = sp;
                else {{
                    if (wR.y < lm[11].y) s_data.top = true;
                    if (s_data.top && wR.y > lm[23].y) s_data.lock = true;

                    if (!s_data.lock) {{
                        let d = Math.abs(sp - s_data.initS);
                        if(d > s_data.pkSp && d < 18) s_data.pkSp = d;
                        document.getElementById('s_sp').innerText = s_data.pkSp.toFixed(1);
                        let kn = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI);
                        if(kn > s_data.pkKn) s_data.pkKn = kn;
                        document.getElementById('s_kn').innerText = s_data.pkKn.toFixed(1);
                    }}
                }}
            }}
        }}

        async function stream(v) {{
            while(!v.paused && !v.ended) {{
                await pose.send({{image: v}});
                await new Promise(r => setTimeout(r, 40));
            }}
        }}

        // [핵심] 모든 재생 시도 시 리셋 및 엔진 재부팅
        vf.onplay = () => {{ 
            initEngine();
            f_data = {{ pkSw:0, pkXF:0, c:0, lock:false, stCX:0, top:false }};
            document.querySelectorAll('#f_sw, #f_xf').forEach(s => s.innerText = "0.0");
            stream(vf); 
        }};

        vs.onplay = () => {{ 
            if(!pose) initEngine();
            s_data = {{ pkSp:0, pkKn:0, c:0, lock:false, initS:0, top:false }};
            document.querySelectorAll('#s_sp, #s_kn').forEach(s => s.innerText = "0.0");
            stream(vs); 
        }};

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
    </script>
    """

f_f = st.file_uploader("정면 영상 업로드", type=['mp4', 'mov'])
s_f = st.file_uploader("측면 영상 업로드", type=['mp4', 'mov'])

if f_f and s_f:
    f_b = base64.b64encode(f_f.read()).decode()
    s_b = base64.b64encode(s_f.read()).decode()
    components.html(get_hot_reload_engine(f_b, s_b), height=1400)
