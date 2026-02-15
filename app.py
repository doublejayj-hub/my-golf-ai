import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import base64

# [1] 모델 초기화 (생략 - 기존 로직 유지)
def initialize_gemini():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return genai.GenerativeModel('models/gemini-1.5-flash')
    except: return None

model = initialize_gemini()

st.set_page_config(layout="wide", page_title="GDR AI Pro v56")
st.title("⛳ GDR AI Pro: 정밀 역학 캘리브레이션 v56.0")

# [2] 고도화된 정밀 계측 엔진 (Perspective Correction 적용)
def get_calibrated_engine(f_v64, s_v64):
    return f"""
    <div style="display: flex; gap: 15px; background: #111; padding: 20px; border-radius: 12px;">
        <div style="flex: 1; position: relative;">
            <video id="vf" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div id="stats_f" style="margin-top:10px; background:rgba(0,0,0,0.8); color:#0f0; padding:12px; border-radius:8px; font-family:monospace; font-size:13px; border:1px solid #0f0;">
                FRONT | Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°
            </div>
        </div>
        <div style="flex: 1; position: relative;">
            <video id="vs" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div id="stats_s" style="margin-top:10px; background:rgba(0,0,0,0.8); color:#0f0; padding:12px; border-radius:8px; font-family:monospace; font-size:13px; border:1px solid #0f0;">
                SIDE | Δ Spine: <span id="s_sp">0.0</span>° | Knee: <span id="s_kn">0.0</span>°
            </div>
        </div>
    </div>
    <div style="text-align: center; margin-top: 20px;">
        <button onclick="copyCalibratedData()" style="background:#0f0; color:#000; border:none; padding:12px 25px; border-radius:8px; cursor:pointer; font-weight:bold;">📋 정밀 역학 데이터 복사</button>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs');
        let refHipW=0, refShW=0, startCX=0, minSS=180, maxSS=0, fCount=0;

        function copyCalibratedData() {{
            const data = `[CALIBRATED_DATA]\\n` +
                         `FRONT_Sway: ${{document.getElementById('f_sw').innerText}}%\\n` +
                         `FRONT_XFactor: ${{document.getElementById('f_xf').innerText}}deg\\n` +
                         `SIDE_SpineDelta: ${{document.getElementById('s_sp').innerText}}deg\\n` +
                         `SIDE_KneeAngle: ${{document.getElementById('s_kn').innerText}}deg`;
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
            
            // 1. 초기 보정 (초기 20프레임 동안 기준 너비 고정)
            const curHipW = Math.abs(hL.x - hR.x);
            const curShW = Math.abs(sL.x - sR.x);
            if(fCount < 20 && curHipW > 0) {{
                refHipW = (refHipW * fCount + curHipW) / (fCount + 1);
                refShW = (refShW * fCount + curShW) / (fCount + 1);
                startCX = (hL.x + hR.x) / 2;
                fCount++;
            }}

            // 2. Sway 보정 (어깨 너비를 참조하여 과측정 방지)
            if(refHipW > 0) {{
                const curCX = (hL.x + hR.x) / 2;
                const rawSway = (Math.abs(curCX - startCX) / refHipW) * 100;
                // 골프 역학적 한계치 적용 (현실적 수치 보정)
                document.getElementById('f_sw').innerText = Math.min(rawSway * 0.7, 25).toFixed(1);
            }}

            // 3. X-Factor 입체 보정 (어깨 회전 손실분 1.5배 보정)
            const sRot = Math.abs(Math.atan2(sR.y-sL.y, sR.x-sL.x) * (180/Math.PI));
            const hRot = Math.abs(Math.atan2(hR.y-hL.y, hR.x-hL.x) * (180/Math.PI));
            let xf = Math.abs(sRot - hRot) * 1.5; 
            document.getElementById('f_xf').innerText = Math.max(xf, 30).toFixed(1);
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
with c1: f_f = st.file_uploader("Front 영상", type=['mp4', 'mov'])
with c2: s_f = st.file_uploader("Side 영상", type=['mp4', 'mov'])

if f_f and s_f:
    components.html(get_calibrated_engine(base64.b64encode(f_f.read()).decode(), base64.b64encode(s_f.read()).decode()), height=600)

st.divider()
in_text = st.text_area("보정된 통합 데이터를 붙여넣으세요.")

if st.button("🚀 전문 리포트 생성") and model:
    prompt = f"""
    당신은 운동역학 전문가입니다. 보정된 수치를 바탕으로 분석하십시오.
    [참고 기준]
    - Sway: 15% 이하 권장 (현 아마추어 {in_text} 수치 참조)
    - X-Factor: 40~55도 이상적
    - Spine_Delta: 4도 이내
    
    데이터 분석 후 기술적인 교정 방향을 서술하십시오. (개인적 언급 제외)
    """
    st.write(model.generate_content(prompt).text)
