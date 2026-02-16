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

st.set_page_config(layout="wide", page_title="GDR AI Pro v90")
st.title("⛳ GDR AI Pro: 초속공 캘리브레이션 v90.0")

# [2] 고정밀 엔진 (초속공 학습 및 로그 복구)
def get_fast_engine(f_v64, s_v64):
    return f"""
    <style>
        .v-container {{ background: #111; padding: 15px; border-radius: 12px; border: 1px solid #333; margin-bottom: 20px; }}
        video {{ width: 100%; border-radius: 10px; background: #000; }}
        .val-box {{ margin-top:10px; color:#0f0; font-family:monospace; font-size:26px; font-weight:bold; background:rgba(0,255,0,0.1); padding:15px; border-radius:8px; border:1px solid #0f0; text-align:center; }}
        #log {{ font-size: 14px; color: #ff0; text-align:center; margin-top: 8px; font-family: sans-serif; min-height: 20px; }}
    </style>

    <div class="v-container">
        <h4 style="color:#0f0; margin:0 0 10px 0;">FRONT VIEW</h4>
        <video id="vf" controls playsinline muted></video>
        <div class="val-box">Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°</div>
    </div>

    <div class="v-container">
        <h4 style="color:#0f0; margin:0 0 10px 0;">SIDE VIEW</h4>
        <video id="vs" controls playsinline muted></video>
        <div class="display val-box">Δ Spine: <span id="s_sp">0.0</span>° | Knee: <span id="s_kn">0.0</span>°</div>
    </div>
    
    <div id="log">상태: 재생 대기 중</div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs'), log=document.getElementById('log');
        let f_pkSw=0, f_pkXF=0, f_c=0, f_lock=false, s_pkSp=0, s_pkKn=0, s_c=0, s_lock=false;
        let f_refH=0, f_stCX=0, s_initS=0, playStartTime=0;

        const pose = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:0, smoothLandmarks:true}});

        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hL=lm[23], hR=lm[24], sL=lm[11], sR=lm[12], wL=lm[15];
            const now = Date.now();

            // [임팩트 래치] 재생 후 0.3초 이후부터만 작동하도록 대폭 단축
            if (!f_lock && (now - playStartTime > 300)) {{
                if (wL.y > hL.y - 0.05) {{ 
                    f_lock = true; s_lock = true; 
                    log.innerHTML = "<b style='color:#f00;'>상태: 임팩트 고정 완료</b>"; 
                    return; 
                }}
            }}

            // [정면 분석] 5프레임 초고속 학습
            if(!f_lock) {{
                if(f_c < 5) {{ 
                    f_refH = Math.abs(hL.x - hR.x) || 0.1; f_stCX = (hL.x+hR.x)/2; f_c++; 
                    log.innerHTML = "상태: 정면 캘리브레이션 (" + f_c + "/5)";
                }} else {{
                    let sw = (((hL.x+hR.x)/2 - f_stCX) / f_refH) * 110;
                    if(sw > f_pkSw && sw < 17) f_pkSw = sw;
                    document.getElementById('f_sw').innerText = f_pkSw.toFixed(1);
                    
                    let xf = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                    if(xf > f_pkXF && xf < 62) f_pkXF = xf;
                    document.getElementById('f_xf').innerText = (f_pkXF * 1.1).toFixed(1);
                    log.innerHTML = "상태: 실시간 데이터 분석 중";
                }}
            }}

            // [측면 분석]
            if(!s_lock) {{
                const hC = (lm[23].y + lm[24].y)/2, sC = (lm[11].y + lm[12].y)/2;
                const sp = Math.abs(Math.atan2(hC-sC, (lm[23].x+lm[24].x)/2 - (lm[11].x+lm[12].x)/2) * 180/Math.PI);
                if(s_c < 5) {{ s_initS = sp; s_c++; }}
                else {{
                    let d = Math.abs(sp - s_initS);
                    if(d > s_pkSp && d < 14) s_pkSp = d;
                    document.getElementById('s_sp').innerText = s_pkSp.toFixed(1);
                }}
                let kn = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI);
                if(kn > s_pkKn) s_pkKn = kn;
                document.getElementById('s_kn').innerText = s_pkKn.toFixed(1);
            }}
        }});

        async function loop(v) {{
            while(!v.paused && !v.ended) {{
                await pose.send({{image: v}});
                await new Promise(r => setTimeout(r, 60));
            }}
        }}

        vf.onplay = () => {{ 
            f_pkSw=0; f_pkXF=0; f_c=0; f_lock=false; 
            s_pkSp=0; s_pkKn=0; s_c=0; s_lock=false;
            playStartTime = Date.now();
            log.innerHTML = "상태: 분석 준비 완료";
            loop(vf); 
        }};
        vs.onplay = () => {{ loop(vs); }};

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
    </script>
    """

# [3] 파일 업로드
f_f = st.file_uploader("Front Video (정면)", type=['mp4', 'mov'])
s_f = st.file_uploader("Side Video (측면)", type=['mp4', 'mov'])

if f_f and s_f:
    f_b = base64.b64encode(f_f.read()).decode()
    s_b = base64.b64encode(s_f.read()).decode()
    components.html(get_fast_engine(f_b, s_b), height=1400)
