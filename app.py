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

st.set_page_config(layout="wide", page_title="GDR AI Pro v85")
st.title("⛳ GDR AI Pro: 즉시 동기화 및 연산 복구 v85.0")

# [2] 고정밀 즉시 동기화 엔진
def get_immediate_sync_engine(f_v64, s_v64):
    return f"""
    <style>
        .v-wrap {{ background: #111; padding: 15px; border-radius: 12px; border: 1px solid #333; margin-bottom: 20px; }}
        video {{ width: 100%; border-radius: 8px; background: #000; }}
        .display {{ margin-top:10px; color:#0f0; font-family:monospace; font-size:24px; font-weight:bold; background:rgba(0,255,0,0.1); padding:15px; border-radius:8px; border:1px solid #0f0; text-align:center; }}
        #debug {{ font-size: 13px; color: #ff0; margin-top: 5px; text-align:center; font-family: sans-serif; }}
    </style>

    <div class="v-wrap">
        <h4 style="color:#0f0; margin:0 0 10px 0;">FRONT VIEW</h4>
        <video id="vf" controls playsinline></video>
        <div class="display">Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°</div>
    </div>

    <div class="v-wrap">
        <h4 style="color:#0f0; margin:0 0 10px 0;">SIDE VIEW</h4>
        <video id="vs" controls playsinline></video>
        <div class="display">Δ Spine: <span id="s_sp">0.0</span>° | Knee: <span id="s_kn">0.0</span>°</div>
    </div>
    
    <div id="debug">상태: 재생 대기 중</div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs'), dbg=document.getElementById('debug');
        // 변수 즉시 초기화
        let f_refH=0, f_stCX=0, f_pkSw=0, f_pkXF=0, f_init=false, f_lock=false;
        let s_initS=0, s_pkSp=0, s_pkKn=0, s_init=false, s_lock=false;

        const pose = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:0, smoothLandmarks:true}});

        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hL=lm[23], hR=lm[24], sL=lm[11], sR=lm[12], wL=lm[15];

            // 1. 하드 래치 (임팩트 시 완전 중단)
            if (wL.y > hL.y - 0.05) {{ f_lock = true; s_lock = true; dbg.innerText = "상태: 임팩트 감지 - 고정됨"; return; }}

            // 2. 정면 실시간 연산
            if(!f_lock) {{
                if(!f_init) {{ 
                    f_refH = Math.abs(hL.x - hR.x) || 0.1; f_stCX = (hL.x + hR.x)/2; f_init = true; 
                    dbg.innerText = "상태: 정면 기준점 설정 완료";
                }}
                let sw = (((hL.x+hR.x)/2 - f_stCX) / f_refH) * 100;
                if(sw > f_pkSw && sw < 20) f_pkSw = sw;
                document.getElementById('f_sw').innerText = f_pkSw.toFixed(1);

                let xf = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                if(xf > f_pkXF && xf < 65) f_pkXF = xf;
                document.getElementById('f_xf').innerText = (f_pkXF * 1.1).toFixed(1);
            }}

            // 3. 측면 실시간 연산
            if(!s_lock) {{
                const hC = (lm[23].y + lm[24].y)/2, sC = (lm[11].y + lm[12].y)/2;
                const sp = Math.abs(Math.atan2(hC-sC, (lm[23].x+lm[24].x)/2 - (lm[11].x+lm[12].x)/2) * 180/Math.PI);
                if(!s_init) {{ s_initS = sp; s_init = true; dbg.innerText = "상태: 측면 기준점 설정 완료"; }}
                
                let d = Math.abs(sp - s_initS);
                if(d > s_pkSp && d < 15) s_pkSp = d;
                document.getElementById('s_sp').innerText = s_pkSp.toFixed(1);

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

        vf.onplay = () => {{ f_init=false; f_pkSw=0; f_pkXF=0; f_lock=false; loop(vf); }};
        vs.onplay = () => {{ s_init=false; s_pkSp=0; s_pkKn=0; s_lock=false; loop(vs); }};

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
    </script>
    """

# [3] UI 구성
f_f = st.file_uploader("정면 영상", type=['mp4', 'mov'])
s_f = st.file_uploader("측면 영상", type=['mp4', 'mov'])

if f_f and s_f:
    f_b = base64.b64encode(f_f.read()).decode()
    s_b = base64.b64encode(s_f.read()).decode()
    components.html(get_immediate_sync_engine(f_b, s_b), height=1400)
