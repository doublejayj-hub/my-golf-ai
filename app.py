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

st.set_page_config(layout="wide", page_title="GDR AI Pro v93")
st.title("⛳ GDR AI Pro: 좌표 바이패스 및 강제 출력 v93.0")

# [2] 초정밀 무손실 엔진 (Direct Coordinate Access)
def get_bypass_engine(f_v64, s_v64):
    return f"""
    <style>
        .v-box {{ background: #111; padding: 20px; border-radius: 15px; border: 1px solid #333; margin-bottom: 25px; }}
        video {{ width: 100%; border-radius: 10px; background: #000; border: 1px solid #444; }}
        .val-disp {{ margin-top:10px; color:#0f0; font-family:monospace; font-size:28px; font-weight:bold; background:rgba(0,0,0,0.3); padding:15px; border-radius:10px; border:2px solid #0f0; text-align:center; }}
        #log {{ font-size: 14px; color: #0f0; text-align:center; padding: 10px; background: #222; border-radius: 8px; margin-bottom: 10px; font-family: sans-serif; }}
    </style>

    <div id="log">시스템 대기 중...</div>
    
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
        let f_pkSw=0, f_pkXF=0, f_c=0, f_lock=false, s_pkSp=0, s_pkKn=0, s_c=0, s_lock=false;
        let f_refH=0.2, f_stCX=0.5, s_initS=0, playStart=0; // 기본값 할당으로 연산 오류 방지

        const pose = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:0, smoothLandmarks:true, minDetectionConfidence:0.3}});

        pose.onResults((r)=>{{
            if(!r.poseLandmarks) {{ log.innerText = "상태: 인물 인식 시도 중..."; return; }}
            const lm = r.poseLandmarks;
            const hL=lm[24], hR=lm[23], sL=lm[12], sR=lm[11], wL=lm[16]; // 인덱스 교차 검증
            const now = Date.now();

            if (!f_lock && (now - playStart > 300)) {{
                if (wL.y > hL.y) {{ f_lock = true; s_lock = true; log.innerText = "상태: 임팩트 감지 고정"; return; }}
            }}

            // [정면] 바이패스 연산: 기준점 학습 없이 즉시 출력 시도
            if(!f_lock) {{
                log.innerText = "상태: 데이터 스트리밍 중 (" + f_c + ")"; f_c++;
                
                // 기준점이 0인 경우 현재 프레임으로 즉시 할당
                if(f_stCX === 0.5) f_stCX = (hL.x + hR.x) / 2;
                
                let sw = (((hL.x + hR.x)/2 - f_stCX) / f_refH) * 150;
                if(sw > f_pkSw && sw < 25) f_pkSw = sw;
                document.getElementById('f_sw').innerText = Math.abs(f_pkSw).toFixed(1);

                let xf = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                if(xf > f_pkXF && xf < 70) f_pkXF = xf;
                document.getElementById('f_xf').innerText = (f_pkXF * 1.1).toFixed(1);
            }}

            // [측면] 바이패스 연산
            if(!s_lock) {{
                const hC = (lm[23].y + lm[24].y)/2, sC = (lm[11].y + lm[12].y)/2;
                const sp = Math.abs(Math.atan2(hC-sC, (lm[23].x+lm[24].x)/2 - (lm[11].x+lm[12].x)/2) * 180/Math.PI);
                if(s_initS === 0) s_initS = sp;
                
                let d = Math.abs(sp - s_initS);
                if(d > s_pkSp && d < 20) s_pkSp = d;
                document.getElementById('s_sp').innerText = s_pkSp.toFixed(1);

                let kn = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI);
                if(kn > s_pkKn) s_pkKn = kn;
                document.getElementById('s_kn').innerText = s_pkKn.toFixed(1);
            }}
        }});

        async function start(v) {{
            while(!v.paused && !v.ended) {{
                await pose.send({{image: v}});
                await new Promise(r => setTimeout(r, 60));
            }}
        }}

        vf.onplay = () => {{ 
            f_pkSw=0; f_pkXF=0; f_c=0; f_lock=false; f_stCX=0.5;
            playStart = Date.now();
            start(vf); 
        }};
        vs.onplay = () => {{ s_pkSp=0; s_pkKn=0; s_lock=false; s_initS=0; start(vs); }};

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        log.innerText = "엔진 준비 완료. 재생을 시작하세요.";
    </script>
    """

# [3] 파일 업로드
f_f = st.file_uploader("Front Video", type=['mp4', 'mov'])
s_f = st.file_uploader("Side Video", type=['mp4', 'mov'])

if f_f and s_f:
    f_b = base64.b64encode(f_f.read()).decode()
    s_b = base64.b64encode(s_f.read()).decode()
    components.html(get_bypass_engine(f_b, s_b), height=1400)
