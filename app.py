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

st.set_page_config(layout="wide", page_title="GDR AI Pro v95")
st.title("⛳ GDR AI Pro: 자세 기반 자동 래치 패치 v95.0")

# [2] 고정밀 분석 엔진 (자세 기반 동적 래칭 시스템)
def get_pose_latch_engine(f_v64, s_v64):
    return f"""
    <style>
        .v-box {{ background: #111; padding: 15px; border-radius: 12px; border: 1px solid #333; margin-bottom: 20px; }}
        video {{ width: 100%; border-radius: 10px; background: #000; }}
        .val-disp {{ margin-top:10px; color:#0f0; font-family:monospace; font-size:26px; font-weight:bold; background:rgba(0,255,0,0.1); padding:15px; border-radius:8px; border:1px solid #0f0; text-align:center; }}
        #log {{ font-size: 14px; color: #ff0; text-align:center; margin: 10px 0; background: #222; padding: 10px; border-radius: 5px; }}
    </style>

    <div id="log">시스템 준비 완료. 영상을 재생하세요.</div>
    
    <div class="v-box">
        <h4 style="color:#0f0; margin:0 0 10px 0;">FRONT (Pose-Based)</h4>
        <video id="vf" controls playsinline muted></video>
        <div class="val-disp">Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°</div>
    </div>

    <div class="v-box">
        <h4 style="color:#0f0; margin:0 0 10px 0;">SIDE (Pose-Based)</h4>
        <video id="vs" controls playsinline muted></video>
        <div class="val-disp">Δ Spine: <span id="s_sp">0.0</span>° | Knee: <span id="s_kn">0.0</span>°</div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs'), log=document.getElementById('log');
        let f_pkSw=0, f_pkXF=0, f_c=0, f_lock=false, s_pkSp=0, s_pkKn=0, s_c=0, s_lock=false;
        let f_refH=0.2, f_stCX=0, s_initS=0;

        const pose = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:0, smoothLandmarks:true, minDetectionConfidence:0.4}});

        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hL=lm[24], hR=lm[23], sL=lm[12], sR=lm[11], wL=lm[16], wR=lm[15];

            // [자세 기반 자동 래치] 양 손 중 하나라도 골반 높이(23,24번) 이하로 내려가면 임팩트로 간주
            // 백스윙 정점(손목이 어깨보다 높음) 이후에만 작동하도록 트리거 정교화
            if (wL.y > Math.min(sL.y, sR.y) && (wL.y > hL.y - 0.05)) {{
                f_lock = true; s_lock = true;
                log.innerHTML = "<b style='color:#0f0;'>상태: 자세 인식 기반 임팩트 고정 완료</b>";
                return;
            }}

            // 정면 분석
            if(!f_lock) {{
                f_c++;
                log.innerText = "상태: 실시간 분석 중 - 프레임 " + f_c;
                if(f_stCX === 0) f_stCX = (hL.x + hR.x) / 2;
                let sw = (((hL.x + hR.x)/2 - f_stCX) / f_refH) * 130;
                if(sw > f_pkSw && sw < 18) f_pkSw = sw;
                document.getElementById('f_sw').innerText = f_pkSw.toFixed(1);
                let xf = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                if(xf > f_pkXF && xf < 65) f_pkXF = xf;
                document.getElementById('f_xf').innerText = (f_pkXF * 1.1).toFixed(1);
            }}

            // 측면 분석
            if(!s_lock) {{
                const hC = (lm[23].y + lm[24].y)/2, sC = (lm[11].y + lm[12].y)/2;
                const sp = Math.abs(Math.atan2(hC-sC, (lm[23].x+lm[24].x)/2 - (lm[11].x+lm[12].x)/2) * 180/Math.PI);
                if(s_initS === 0) s_initS = sp;
                let d = Math.abs(sp - s_initS);
                if(d > s_pkSp && d < 15) s_pkSp = d;
                document.getElementById('s_sp').innerText = s_pkSp.toFixed(1);
                let kn = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI);
                if(kn > s_pkKn) s_pkKn = kn;
                document.getElementById('s_kn').innerText = s_pkKn.toFixed(1);
            }}
        }});

        // [핵심] 프레임 단위 강제 대기 루프 (병목 현상 해결)
        async function runSync(v) {{
            while(!v.paused && !v.ended) {{
                await pose.send({{image: v}}); // 엔진이 프레임을 다 처리할 때까지 대기
                await new Promise(r => setTimeout(r, 40)); // 브라우저 UI 갱신을 위한 최소 시간 확보
            }}
        }}

        vf.onplay = () => {{ 
            f_pkSw=0; f_pkXF=0; f_c=0; f_lock=false; f_stCX=0;
            s_pkSp=0; s_pkKn=0; s_lock=false; s_initS=0;
            runSync(vf); 
        }};
        vs.onplay = () => {{ runSync(vs); }};

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
    components.html(get_pose_latch_engine(f_b, s_b), height=1400)
