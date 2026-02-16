import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import base64

# [1] 모델 초기화
def initialize_gemini():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return genai.GenerativeModel('models/gemini-1.5-flash')
    except: return None

model = initialize_gemini()

st.set_page_config(layout="wide", page_title="GDR AI Pro v94")
st.title("⛳ GDR AI Pro: 메모리 퍼지 및 UI 무결성 패치 v94.0")

# [2] 고정밀 엔진 (메모리 강제 초기화 및 로그 우선 출력)
def get_purge_engine(f_v64, s_v64):
    return f"""
    <style>
        .v-container {{ background: #000; padding: 20px; border-radius: 15px; border: 1px solid #333; margin-bottom: 25px; }}
        video {{ width: 100%; border-radius: 10px; background: #000; border: 1px solid #444; }}
        .val-disp {{ margin-top:15px; color:#0f0; font-family:monospace; font-size:28px; font-weight:bold; background:rgba(0,0,0,0.4); padding:20px; border-radius:10px; border:2px solid #0f0; text-align:center; box-shadow: 0 0 10px rgba(0,255,0,0.2); }}
        #log {{ font-size: 16px; color: #ff0; text-align:center; padding: 12px; background: #222; border-radius: 8px; margin-bottom: 10px; font-family: sans-serif; font-weight: bold; }}
    </style>

    <div id="log">시스템 대기 중... 재생 버튼을 눌러주세요.</div>
    
    <div class="v-container">
        <video id="vf" controls playsinline muted></video>
        <div class="val-disp">Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°</div>
    </div>

    <div class="v-container">
        <video id="vs" controls playsinline muted></video>
        <div class="val-disp">Δ Spine: <span id="s_sp">0.0</span>° | Knee: <span id="s_kn">0.0</span>°</div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs'), log=document.getElementById('log');
        let f_pkSw=0, f_pkXF=0, f_c=0, f_lock=false, s_pkSp=0, s_pkKn=0, s_c=0, s_lock=false;
        let f_refH=0.2, f_stCX=0, s_initS=0, playStart=0;

        const pose = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:0, smoothLandmarks:true, minDetectionConfidence:0.4}});

        // [핵심] 로그 출력을 비동기로 분리하여 UI 멈춤 방지
        function updateUI(id, val) {{
            requestAnimationFrame(() => {{
                const el = document.getElementById(id);
                if(el) el.innerText = val;
            }});
        }}

        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hL=lm[24], hR=lm[23], sL=lm[12], sR=lm[11], wL=lm[16];
            const now = Date.now();

            // 1. 임팩트 래치 로직
            if (!f_lock && (now - playStart > 400)) {{
                if (wL.y > hL.y - 0.05) {{ 
                    f_lock = true; s_lock = true; 
                    log.innerText = "상태: 임팩트 고정됨"; 
                    return; 
                }}
            }}

            // 2. 정면 분석 (카운터 및 수치 강제 주입)
            if(!f_lock) {{
                f_c++;
                log.innerText = "상태: 실시간 분석 카운트 " + f_c;
                
                if(f_stCX === 0) f_stCX = (hL.x + hR.x) / 2;
                
                let sw = (((hL.x + hR.x)/2 - f_stCX) / f_refH) * 140;
                if(sw > f_pkSw && sw < 20) f_pkSw = sw;
                updateUI('f_sw', f_pkSw.toFixed(1));

                let xf = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                if(xf > f_pkXF && xf < 65) f_pkXF = xf;
                updateUI('f_xf', (f_pkXF * 1.1).toFixed(1));
            }}

            // 3. 측면 분석
            if(!s_lock) {{
                const hC = (lm[23].y + lm[24].y)/2, sC = (lm[11].y + lm[12].y)/2;
                const sp = Math.abs(Math.atan2(hC-sC, (lm[23].x+lm[24].x)/2 - (lm[11].x+lm[12].x)/2) * 180/Math.PI);
                if(s_initS === 0) s_initS = sp;
                
                let d = Math.abs(sp - s_initS);
                if(d > s_pkSp && d < 15) s_pkSp = d;
                updateUI('s_sp', s_pkSp.toFixed(1));

                let kn = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI);
                if(kn > s_pkKn) s_pkKn = kn;
                updateUI('s_kn', s_pkKn.toFixed(1));
            }}
        }});

        async function startAnalysis(v) {{
            while(!v.paused && !v.ended) {{
                await pose.send({{image: v}});
                await new Promise(r => setTimeout(r, 60));
            }}
        }}

        // [핵심] 재생 시 물리적 메모리 퍼지
        vf.onplay = () => {{ 
            f_pkSw=0; f_pkXF=0; f_c=0; f_lock=false; f_stCX=0;
            s_pkSp=0; s_pkKn=0; s_lock=false; s_initS=0;
            playStart = Date.now();
            updateUI('f_sw', '0.0'); updateUI('f_xf', '0.0');
            updateUI('s_sp', '0.0'); updateUI('s_kn', '0.0');
            startAnalysis(vf); 
        }};
        vs.onplay = () => {{ startAnalysis(vs); }};

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
    </script>
    """

# [3] UI
f_f = st.file_uploader("Front Video (정면)", type=['mp4', 'mov'])
s_f = st.file_uploader("Side Video (측면)", type=['mp4', 'mov'])

if f_f and s_f:
    f_b = base64.b64encode(f_f.read()).decode()
    s_b = base64.b64encode(s_f.read()).decode()
    components.html(get_purge_engine(f_b, s_b), height=1400)
