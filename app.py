import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import base64

# [1] 모델 초기화 (안정성 우선)
def initialize_gemini():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for name in ['models/gemini-1.5-flash', 'models/gemini-pro']:
            if name in models: return genai.GenerativeModel(name)
        return genai.GenerativeModel(models[0]) if models else None
    except: return None

model = initialize_gemini()

st.set_page_config(layout="wide", page_title="GDR AI Engine v54")
st.title("⛳ GDR AI Pro: 고정밀 역학 계측 v54.0")

# [2] 정밀 보정 엔진 (Reference 고정 및 노이즈 필터링 강화)
def get_calibrated_engine(f_v64, s_v64):
    return f"""
    <div style="display: flex; gap: 15px; background: #000; padding: 15px; border-radius: 12px;">
        <div style="flex: 1; position: relative;">
            <video id="vf" controls playsinline style="width: 100%; border: 1px solid #444;"></video>
            <div id="stats_f" style="color: #0f0; font-family: monospace; font-size: 12px; margin-top:5px;">
                FRONT | Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°
            </div>
        </div>
        <div style="flex: 1; position: relative;">
            <video id="vs" controls playsinline style="width: 100%; border: 1px solid #444;"></video>
            <div id="stats_s" style="color: #0f0; font-family: monospace; font-size: 12px; margin-top:5px;">
                SIDE | Δ Spine: <span id="s_sp">0.0</span>° | Knee: <span id="s_kn">0.0</span>°
            </div>
        </div>
    </div>
    <div style="text-align: center; margin-top: 15px;">
        <button onclick="copyCalibratedData()" style="background:#0f0; color:#000; border:none; padding:12px 25px; border-radius:8px; cursor:pointer; font-weight:bold;">📋 정밀 분석 데이터 복사</button>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs');
        let refHipWidth=0, startX=0, minS=180, maxS=0, frameCount=0;

        function copyCalibratedData() {{
            const data = `[CALIBRATED_SWING_DATA]\\n` +
                         `FRONT_Sway_Ratio: ${{document.getElementById('f_sw').innerText}}%\\n` +
                         `FRONT_X_Factor: ${{document.getElementById('f_xf').innerText}}deg\\n` +
                         `SIDE_Spine_Delta: ${{document.getElementById('s_sp').innerText}}deg\\n` +
                         `SIDE_Knee_Angle: ${{document.getElementById('s_kn').innerText}}deg`;
            navigator.clipboard.writeText(data);
            alert("보정된 데이터가 복사되었습니다.");
        }}

        const poseF = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        const poseS = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        [poseF, poseS].forEach(p => p.setOptions({{modelComplexity:1, smoothLandmarks:true}}));

        poseF.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hL=lm[23], hR=lm[24], sL=lm[11], sR=lm[12];
            
            // 1. Reference 고정 로직 (초기 10프레임 동안 기준 골반 너비 측정)
            const curHipW = Math.abs(hL.x - hR.x);
            if(frameCount < 10) {{
                refHipWidth = (refHipWidth * frameCount + curHipW) / (frameCount + 1);
                startX = (hL.x + hR.x) / 2;
                frameCount++;
            }}

            // 2. 정규화된 Sway (고정 Ref값 대비)
            const curCX = (hL.x + hR.x) / 2;
            const sway = (Math.abs(curCX - startX) / refHipWidth) * 100;
            document.getElementById('f_sw').innerText = Math.min(sway, 30).toFixed(1); // 30% 이상은 이상치로 컷

            // 3. X-Factor (상하체 각도 차이 보정)
            const sRot = Math.atan2(sR.y-sL.y, sR.x-sL.x)*180/Math.PI;
            const hRot = Math.atan2(hR.y-hL.y, hR.x-hL.x)*180/PI;
            document.getElementById('f_xf').innerText = Math.abs(sRot - hRot).toFixed(1);
        }});

        poseS.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hC = {{x:(lm[23].x+lm[24].x)/2, y:(lm[23].y+lm[24].y)/2}};
            const sC = {{x:(lm[11].x+lm[12].x)/2, y:(lm[11].y+lm[12].y)/2}};
            const curS = Math.abs(Math.atan2(hC.y-sC.y, hC.x-sC.x)*180/Math.PI);
            
            // 데이터 튐 방지 (안정화)
            if(curS > 50 && curS < 130) {{ 
                if(curS < minS) minS = curS;
                if(curS > maxS) maxS = curS;
                document.getElementById('s_sp').innerText = (maxS - minS).toFixed(1);
            }}
            document.getElementById('s_kn').innerText = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI).toFixed(1);
        }});

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        
        vf.onplay = async () => {{ while(!vf.paused){{ await poseF.send({{image:vf}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
        vs.onplay = async () => {{ while(!vs.paused){{ await poseS.send({{image:vs}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
    </script>
    """

# [3] 레이아웃 및 리포트
c1, c2 = st.columns(2)
with c1: f_f = st.file_uploader("정면 업로드", type=['mp4', 'mov'])
with c2: s_f = st.file_uploader("측면 업로드", type=['mp4', 'mov'])

if f_f and s_f:
    components.html(get_calibrated_engine(base64.b64encode(f_f.read()).decode(), base64.b64encode(s_f.read()).decode()), height=550)

st.divider()
in_data = st.text_area("보정된 데이터를 붙여넣으세요.")

if st.button("🚀 정밀 역학 분석 시작") and model:
    prompt = f"""
    당신은 운동역학 전문가입니다. 다음의 '보정된(Calibrated)' 데이터를 바탕으로 기술 진단을 수행하십시오.
    [수치 가이드] 
    - Sway: 15% 이상 시 축 무너짐.
    - X-Factor: 40-55도 프로 수준, 60도 이상 시 과도한 꼬임.
    - Spine_Delta: 4도 이내가 이상적.
    
    [사용자 데이터]
    {in_data}
    
    데이터 간 인과관계를 물리적으로 분석하여 교정 방향을 제시하십시오.
    """
    st.write(model.generate_content(prompt).text)
