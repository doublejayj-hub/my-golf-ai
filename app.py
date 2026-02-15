import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import base64

# [1] Gemini 모델 초기화
def initialize_gemini():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return genai.GenerativeModel('models/gemini-1.5-flash')
    except: return None

model = initialize_gemini()

st.set_page_config(layout="wide", page_title="GDR AI Pro v81")
st.title("⛳ GDR AI Pro: UI 최적화 및 조작성 패치 v81.0")

# [2] 대화면 UI 및 엔진 통합 (영상 사이즈 확대)
def get_large_ui_engine(f_v64, s_v64):
    return f"""
    <style>
        .video-container {{
            background: #111;
            padding: 15px;
            border-radius: 15px;
            border: 2px solid #333;
            margin-bottom: 15px;
        }}
        video {{
            width: 100%;
            height: auto;
            max-height: 500px; /* 시인성 확보를 위한 높이 확대 */
            border-radius: 10px;
            background: #000;
        }}
        .stat-box {{
            margin-top: 15px;
            background: rgba(0, 255, 0, 0.1);
            color: #0f0;
            padding: 20px;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            font-size: 20px; /* 수치 가독성 확대 */
            border: 1px solid #0f0;
            font-weight: bold;
        }}
        #status {{
            color: #888;
            font-size: 14px;
            margin-top: 10px;
            text-align: center;
        }}
    </style>

    <div style="display: flex; flex-direction: column; gap: 20px;">
        <div class="video-container">
            <h3 style="color: #0f0; margin: 0 0 10px 0;">FRONT VIEW</h3>
            <video id="vf" controls playsinline></video>
            <div class="stat-box">
                Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°
            </div>
        </div>
        
        <div class="video-container">
            <h3 style="color: #0f0; margin: 0 0 10px 0;">SIDE VIEW</h3>
            <video id="vs" controls playsinline></video>
            <div class="stat-box">
                Δ Spine: <span id="s_sp">0.0</span>° | Knee: <span id="s_kn">0.0</span>°
            </div>
        </div>
    </div>
    
    <div id="status">준비 완료. 영상의 재생 버튼을 눌러주세요.</div>
    <div style="text-align: center; margin-top: 20px;">
        <button onclick="copyData()" style="background:#0f0; color:#000; border:none; padding:15px 40px; border-radius:10px; cursor:pointer; font-weight:bold; font-size:18px;">📋 데이터 복사</button>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs'), st=document.getElementById('status');
        let f_pkSw=0, f_pkXF=0, f_c=0, f_lock=false, s_pkSp=0, s_pkKn=0, s_c=0, s_lock=false;
        let f_refH=0, f_stCX=0, s_minS=0, s_maxS=0;

        const pose = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:0, smoothLandmarks:true}});

        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            st.innerText = "분석 엔진 가동 중...";
            const lm = r.poseLandmarks;
            const hL=lm[23], hR=lm[24], sL=lm[11], sR=lm[12], wL=lm[15];

            if (wL.y > hL.y - 0.05) {{ f_lock = true; s_lock = true; st.innerText = "임팩트 구간 도달 - 수치 고정됨"; return; }}

            if(!f_lock) {{
                if(f_c < 15) {{ f_refH = Math.abs(hL.x - hR.x); f_stCX = (hL.x+hR.x)/2; f_c++; }}
                else {{
                    let sw = (((hL.x+hR.x)/2 - f_stCX) / f_refH) * 100;
                    if(sw > f_pkSw && sw < 17) f_pkSw = sw;
                    document.getElementById('f_sw').innerText = f_pkSw.toFixed(1);
                    let xf = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                    if(xf > f_pkXF && xf < 60) f_pkXF = xf;
                    document.getElementById('f_xf').innerText = (f_pkXF * 1.1).toFixed(1);
                }}
            }}

            if(!s_lock) {{
                const hC = (lm[23].y + lm[24].y)/2, sC = (lm[11].y + lm[12].y)/2;
                const sp = Math.abs(Math.atan2(hC-sC, (lm[23].x+lm[24].x)/2 - (lm[11].x+lm[12].x)/2) * 180/Math.PI);
                if(s_c < 10) {{ s_minS = sp; s_maxS = sp; s_c++; }}
                else {{
                    if(sp < s_minS) s_minS = sp; if(sp > s_maxS) s_maxS = sp;
                    let d = s_maxS - s_minS;
                    if(d > s_pkSp && d < 14) s_pkSp = d;
                    document.getElementById('s_sp').innerText = s_pkSp.toFixed(1);
                }}
                let kn = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI);
                if(kn > s_pkKn) s_pkKn = kn;
                document.getElementById('s_kn').innerText = s_pkKn.toFixed(1);
            }}
        }});

        async function run(v) {{
            while(!v.paused && !v.ended) {{
                await pose.send({{image: v}});
                await new Promise(r => setTimeout(r, 80));
            }}
        }}

        function copyData() {{
            const res = `[GDR_FINAL]\\nF_Sway: ${{document.getElementById('f_sw').innerText}}%\\nF_XF: ${{document.getElementById('f_xf').innerText}}deg\\nS_Spine: ${{document.getElementById('s_sp').innerText}}deg\\nS_Knee: ${{document.getElementById('s_kn').innerText}}deg`;
            navigator.clipboard.writeText(res); alert("데이터 복사 완료");
        }}

        vf.onplay = () => {{ f_pkSw=0; f_pkXF=0; f_c=0; f_lock=false; run(vf); }};
        vs.onplay = () => {{ s_pkSp=0; s_pkKn=0; s_c=0; s_lock=false; run(vs); }};

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
    </script>
    """

# [3] 파일 업로드
f_f = st.file_uploader("Front Video", type=['mp4', 'mov'])
s_f = st.file_uploader("Side Video", type=['mp4', 'mov'])

if f_f and s_f:
    f_b = base64.b64encode(f_f.read()).decode()
    s_b = base64.b64encode(s_f.read()).decode()
    # height를 충분히 확보하여 스크롤 없이 조작 가능하게 함
    components.html(get_large_ui_engine(f_b, s_b), height=1400)

st.divider()
in_text = st.text_area("데이터를 붙여넣으세요.")
if st.button("🚀 종합 분석 시작"):
    st.write(model.generate_content(f"전문가 분석: {in_text}").text)
