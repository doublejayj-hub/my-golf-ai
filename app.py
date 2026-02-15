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

st.set_page_config(layout="wide", page_title="GDR AI Pro v82")
st.title("⛳ GDR AI Pro: 강제 프레임 추출 및 무결성 패치 v82.0")

# [2] 고정밀 분석 엔진 (프레임 강제 동기화)
def get_step_engine(f_v64, s_v64):
    return f"""
    <style>
        .video-wrap {{ background: #111; padding: 15px; border-radius: 12px; border: 1px solid #333; margin-bottom: 20px; }}
        video {{ width: 100%; height: auto; border-radius: 8px; background: #000; }}
        .stat-display {{ margin-top:10px; color:#0f0; font-family:monospace; font-size:18px; font-weight:bold; background:rgba(0,255,0,0.1); padding:15px; border-radius:8px; border:1px solid #0f0; }}
        #log {{ font-size: 12px; color: #555; margin-top: 5px; text-align: center; }}
    </style>

    <div class="video-wrap">
        <h4 style="color:#0f0; margin:0 0 10px 0;">FRONT VIEW (Scanning...)</h4>
        <video id="vf" controls playsinline></video>
        <div class="stat-display">Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°</div>
    </div>

    <div class="video-wrap">
        <h4 style="color:#0f0; margin:0 0 10px 0;">SIDE VIEW (Scanning...)</h4>
        <video id="vs" controls playsinline></video>
        <div class="stat-display">Δ Spine: <span id="s_sp">0.0</span>° | Knee: <span id="s_kn">0.0</span>°</div>
    </div>
    
    <div id="log">시스템 준비 완료. 영상을 재생하면 추출이 시작됩니다.</div>
    <div style="text-align: center; margin-top: 20px;">
        <button onclick="copyData()" style="background:#0f0; color:#000; border:none; padding:15px 40px; border-radius:10px; cursor:pointer; font-weight:bold; font-size:18px;">📋 데이터 복사</button>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs'), log=document.getElementById('log');
        let f_pkSw=0, f_pkXF=0, f_c=0, f_lock=false, s_pkSp=0, s_pkKn=0, s_c=0, s_lock=false;
        let f_refH=0, f_stCX=0, s_minS=0, s_maxS=0;

        const pose = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:0, smoothLandmarks:true}});

        // [핵심] 수치 추출 로직 무결성 강화
        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            log.innerText = "상태: 관절 인식 및 연산 중...";
            const lm = r.poseLandmarks;
            const hL=lm[23], hR=lm[24], sL=lm[11], sR=lm[12], wL=lm[15];

            if (wL.y > hL.y - 0.03) {{ f_lock = true; s_lock = true; log.innerText = "임팩트 시점 데이터 고정 완료"; return; }}

            if(!f_lock) {{
                if(f_c < 15) {{ f_refH = Math.abs(hL.x - hR.x); f_stCX = (hL.x+hR.x)/2; f_c++; }}
                else if(f_refH > 0) {{
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

        // [사전검증] 프레임 단위 강제 전송 엔진
        async function runScan(v) {{
            while(!v.paused && !v.ended) {{
                try {{
                    await pose.send({{image: v}});
                }} catch(e) {{
                    console.error("Frame skip");
                }}
                await new Promise(r => setTimeout(r, 100)); // 연산 부하 방지용 딜레이
            }}
        }}

        function copyData() {{
            const res = `[GDR_V82]\\nF_Sway: ${{document.getElementById('f_sw').innerText}}%\\nF_XF: ${{document.getElementById('f_xf').innerText}}deg\\nS_Spine: ${{document.getElementById('s_sp').innerText}}deg\\nS_Knee: ${{document.getElementById('s_kn').innerText}}deg`;
            navigator.clipboard.writeText(res); alert("데이터가 복사되었습니다.");
        }}

        vf.onplay = () => {{ f_pkSw=0; f_pkXF=0; f_c=0; f_lock=false; runScan(vf); }};
        vs.onplay = () => {{ s_pkSp=0; s_pkKn=0; s_c=0; s_lock=false; runScan(vs); }};

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
    </script>
    """

# [3] UI 구성
f_file = st.file_uploader("Front Video (정면)", type=['mp4', 'mov'])
s_file = st.file_uploader("Side Video (측면)", type=['mp4', 'mov'])

if f_file and s_file:
    f_b = base64.b64encode(f_file.read()).decode()
    s_b = base64.b64encode(s_file.read()).decode()
    components.html(get_step_engine(f_b, s_b), height=1400)

st.divider()
in_text = st.text_area("복사된 데이터를 여기에 붙여넣으세요.")
if st.button("🚀 종합 역학 분석 리포트 생성"):
    st.write(model.generate_content(f"운동역학 전문가로서 기술 분석 수행: {in_text}").text)
