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

st.set_page_config(layout="wide", page_title="GDR AI Pro v79")
st.title("⛳ GDR AI Pro: 엔진 복구 및 구간 하드 래치 v79.0")

# [2] 초정밀 무결성 분석 엔진
def get_integrity_engine(f_v64, s_v64):
    return f"""
    <div style="display: flex; gap: 10px; background: #111; padding: 20px; border-radius: 12px; border: 1px solid #333;">
        <div style="flex: 1; text-align: center;">
            <video id="vf" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div style="margin-top:10px; color:#0f0; font-family:monospace; font-size:16px; background:rgba(0,255,0,0.1); padding:10px;">
                Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°
            </div>
        </div>
        <div style="flex: 1; text-align: center;">
            <video id="vs" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div style="margin-top:10px; color:#0f0; font-family:monospace; font-size:16px; background:rgba(0,255,0,0.1); padding:10px;">
                Δ Spine: <span id="s_sp">0.0</span>° | Knee: <span id="s_kn">0.0</span>°
            </div>
        </div>
    </div>
    <div id="log" style="margin-top:10px; padding:8px; background:#000; color:#555; font-size:11px; font-family:monospace;">상태: 엔진 대기 중...</div>
    <div style="text-align: center; margin-top: 15px;">
        <button onclick="copyData()" style="background:#0f0; color:#000; border:none; padding:12px 25px; border-radius:8px; cursor:pointer; font-weight:bold;">📋 결과 복사</button>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs'), log=document.getElementById('log');
        let f_refH=0, f_startCX=0, f_pkSw=0, f_pkXF=0, f_c=0, f_lock=false;
        let s_minS=0, s_maxS=0, s_pkSp=0, s_pkKn=0, s_c=0, s_lock=false;

        function copyData() {{
            const res = `[ANALYSIS]\\nF_Sway: ${{document.getElementById('f_sw').innerText}}%\\nF_XF: ${{document.getElementById('f_xf').innerText}}deg\\nS_Spine: ${{document.getElementById('s_sp').innerText}}deg\\nS_Knee: ${{document.getElementById('s_kn').innerText}}deg`;
            navigator.clipboard.writeText(res); alert("복사 완료");
        }}

        // 인스턴스 하나로 고정하여 충돌 방지
        const pose = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:0, smoothLandmarks:true}});

        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            log.innerText = "상태: 연산 가동 중"; log.style.color = "#0f0";
            const lm = r.poseLandmarks;
            const hL=lm[23], hR=lm[24], sL=lm[11], sR=lm[12];
            const wL=lm[15];

            // 1. 임팩트 하드 래치 (손목 위치 기준)
            if (wL.y > hL.y - 0.05) {{ f_lock = true; s_lock = true; return; }}

            // 2. 정면 데이터 추출 (정합성 보정)
            if(!f_lock) {{
                if(f_c < 15) {{ 
                    f_refH = Math.abs(hL.x - hR.x); f_startCX = (hL.x + hR.x)/2; f_c++; 
                }} else {{
                    let sw = (((hL.x+hR.x)/2 - f_startCX) / f_refH) * 100;
                    if(sw > f_pkSw && sw < 17) f_pkSw = sw;
                    document.getElementById('f_sw').innerText = f_pkSw.toFixed(1);

                    let xf = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                    if(xf > f_pkXF && xf < 60) f_pkXF = xf;
                    document.getElementById('f_xf').innerText = (f_pkXF * 1.1).toFixed(1);
                }}
            }}

            // 3. 측면 데이터 추출 (피니시 오염 차단)
            if(!s_lock) {{
                const hC = (lm[23].y + lm[24].y)/2, sC = (lm[11].y + lm[12].y)/2;
                const sp = Math.abs(Math.atan2(hC - sC, (lm[23].x+lm[24].x)/2 - (lm[11].x+lm[12].x)/2) * 180/Math.PI);
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

        async function startEngine(v) {{
            while(!v.paused && !v.ended) {{
                await pose.send({{image: v}});
                await new Promise(r => setTimeout(r, 80)); // 안정적인 12fps 추출
            }}
        }}

        vf.onplay = () => {{ f_lock=false; s_lock=false; f_c=0; s_c=0; f_pkSw=0; f_pkXF=0; s_pkSp=0; startEngine(vf); }};
        vs.onplay = () => {{ startEngine(vs); }};
        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
    </script>
    """

# [3] 파일 업로드
f_f = st.file_uploader("정면 영상", type=['mp4', 'mov'])
s_f = st.file_uploader("측면 영상", type=['mp4', 'mov'])

if f_f and s_f:
    f_b = base64.b64encode(f_f.read()).decode()
    s_b = base64.b64encode(s_f.read()).decode()
    components.html(get_integrity_engine(f_b, s_b), height=550)

st.divider()
in_text = st.text_area("분석 데이터를 붙여넣으세요.")
if st.button("🚀 종합 분석 시작"):
    st.write(model.generate_content(f"전문가 역학 분석: {in_text}").text)
