import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import base64

# [1] 모델 초기화
def initialize_gemini():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]
        return genai.GenerativeModel(target)
    except: return None

model = initialize_gemini()

st.set_page_config(layout="wide", page_title="GDR AI Debugged v55")
st.title("⛳ GDR AI Pro: 정면 데이터 추출 디버깅 v55.0")

# [2] 디버깅된 통합 엔진 (Sway/X-Factor 로직 강화)
def get_debugged_engine(f_v64, s_v64):
    return f"""
    <div style="display: flex; gap: 15px; background: #111; padding: 20px; border-radius: 12px; border: 1px solid #333;">
        <div style="flex: 1; position: relative; text-align: center;">
            <h4 style="color: #0f0; margin-bottom: 10px;">FRONT VIEW</h4>
            <video id="vf" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div id="stats_f" style="margin-top:10px; background:rgba(0,255,0,0.1); color:#0f0; padding:12px; border-radius:8px; font-family:monospace; font-size:14px; border:1px solid #0f0;">
                Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°
            </div>
        </div>
        <div style="flex: 1; position: relative; text-align: center;">
            <h4 style="color: #0f0; margin-bottom: 10px;">SIDE VIEW</h4>
            <video id="vs" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div id="stats_s" style="margin-top:10px; background:rgba(0,255,0,0.1); color:#0f0; padding:12px; border-radius:8px; font-family:monospace; font-size:14px; border:1px solid #0f0;">
                Δ Spine: <span id="s_sp">0.0</span>° | Knee: <span id="s_kn">0.0</span>°
            </div>
        </div>
    </div>
    <div style="text-align: center; margin-top: 20px;">
        <button onclick="copyData()" style="background:#0f0; color:#000; border:none; padding:15px 30px; border-radius:10px; cursor:pointer; font-weight:bold; font-size:16px; box-shadow: 0 4px 15px rgba(0,255,0,0.3);">📋 통합 역학 데이터 복사</button>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs');
        let refHipW=0, startXF=0, minSS=180, maxSS=0, fCount=0;

        function copyData() {{
            const fsw = document.getElementById('f_sw').innerText;
            const fxf = document.getElementById('f_xf').innerText;
            const ssp = document.getElementById('s_sp').innerText;
            const skn = document.getElementById('s_kn').innerText;
            const data = `[ANALYSIS_REPORT]\\nFRONT_Sway: ${{fsw}}%\\nFRONT_XFactor: ${{fxf}}deg\\nSIDE_SpineDelta: ${{ssp}}deg\\nSIDE_KneeAngle: ${{skn}}deg`;
            navigator.clipboard.writeText(data);
            alert("디버깅된 데이터가 클립보드에 복사되었습니다.");
        }}

        const poseF = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        const poseS = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        [poseF, poseS].forEach(p => p.setOptions({{modelComplexity:1, smoothLandmarks:true}}));

        // [디버깅] 정면 연산 로직 무결성 검증
        poseF.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hL=lm[23], hR=lm[24], sL=lm[11], sR=lm[12];
            
            // 1. 기준 너비 측정 (Calibration)
            const curW = Math.sqrt(Math.pow(hL.x-hR.x, 2) + Math.pow(hL.y-hR.y, 2));
            if(fCount < 15 && curW > 0) {{
                refHipW = (refHipW * fCount + curW) / (fCount + 1);
                startXF = (hL.x + hR.x) / 2;
                fCount++;
            }}

            // 2. Sway Ratio 계산 (보정된 Ref 사용)
            if(refHipW > 0) {{
                const curCX = (hL.x + hR.x) / 2;
                const swayVal = (Math.abs(curCX - startXF) / refHipW) * 100;
                document.getElementById('f_sw').innerText = Math.min(swayVal, 40).toFixed(1);
            }}

            // 3. X-Factor 계산 (디버깅 완료)
            const sRot = Math.atan2(sR.y-sL.y, sR.x-sL.x) * (180/Math.PI);
            const hRot = Math.atan2(hR.y-hL.y, hR.x-hL.x) * (180/Math.PI);
            document.getElementById('f_xf').innerText = Math.abs(sRot - hRot).toFixed(1);
        }});

        poseS.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hC = {{x:(lm[23].x+lm[24].x)/2, y:(lm[23].y+lm[24].y)/2}};
            const sC = {{x:(lm[11].x+lm[12].x)/2, y:(lm[11].y+lm[12].y)/2}};
            const curS = Math.abs(Math.atan2(hC.y-sC.y, hC.x-sC.x)*180/Math.PI);
            if(curS > 40 && curS < 140) {{
                if(curS < minSS) minSS = curS; if(curS > maxSS) maxSS = curS;
                document.getElementById('s_sp').innerText = (maxSS - minSS).toFixed(1);
            }}
            document.getElementById('s_kn').innerText = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI).toFixed(1);
        }});

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        
        vf.onplay = async () => {{ while(!vf.paused){{ await poseF.send({{image:vf}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
        vs.onplay = async () => {{ while(!vs.paused){{ await poseS.send({{image:vs}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
    </script>
    """

# [3] 파일 업로드 및 분석
c1, c2 = st.columns(2)
with c1: f_file = st.file_uploader("정면 영상 (Front)", type=['mp4', 'mov'])
with c2: s_file = st.file_uploader("측면 영상 (Side)", type=['mp4', 'mov'])

if f_file and s_file:
    f_b64 = base64.b64encode(f_file.read()).decode()
    s_b64 = base64.b64encode(s_file.read()).decode()
    components.html(get_debugged_engine(f_b64, s_b64), height=650)

st.divider()
st.header("🔬 기술 역학 데이터 통합 리포트")
in_text = st.text_area("복사한 데이터를 붙여넣으세요.")

if st.button("🚀 종합 분석 리포트 생성") and model:
    prompt = f"""
    당신은 운동역학 전문가입니다. 다음의 '디버깅된' 기술 데이터를 분석하십시오.
    [데이터 정의]
    - FRONT_Sway: 0-15% 정상. 20% 이상 시 축 무너짐.
    - FRONT_XFactor: 상하체 비틀림 강도. (40-60도 권장)
    - SIDE_SpineDelta: 척추각 변화. (4도 이내 권장)
    
    [입력 데이터]
    {in_text}
    
    수치들의 상관관계를 분석하여 기술적인 교정 방향을 제시하십시오.
    """
    st.write(model.generate_content(prompt).text)
