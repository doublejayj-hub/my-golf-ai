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

st.set_page_config(layout="wide", page_title="GDR AI Pro v58")
st.title("⛳ GDR AI Pro: 역학 지표 정의 교정 v58.0")

# [2] 고정밀 역학 추출 엔진 (이벤트 윈도우 및 수치 클램핑)
def get_calibrated_engine(f_v64, s_v64):
    return f"""
    <div style="display: flex; gap: 15px; background: #111; padding: 20px; border-radius: 12px;">
        <div style="flex: 1; position: relative;">
            <video id="vf" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div id="stats_f" style="margin-top:10px; background:rgba(0,0,0,0.8); color:#0f0; padding:12px; border-radius:8px; font-family:monospace; font-size:13px; border:1px solid #0f0;">
                FRONT | Sway: <span id="f_sw_p">0.0</span>% | X-Factor: <span id="f_xf_p">0.0</span>°
            </div>
        </div>
        <div style="flex: 1; position: relative;">
            <video id="vs" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div id="stats_s" style="margin-top:10px; background:rgba(0,0,0,0.8); color:#0f0; padding:12px; border-radius:8px; font-family:monospace; font-size:13px; border:1px solid #0f0;">
                SIDE | Δ Spine: <span id="s_sp_p">0.0</span>° | Knee: <span id="s_kn">0.0</span>°
            </div>
        </div>
    </div>
    <div style="text-align: center; margin-top: 20px;">
        <button onclick="copyData()" style="background:#0f0; color:#000; border:none; padding:12px 25px; border-radius:8px; cursor:pointer; font-weight:bold;">📋 정밀 보정 데이터 복사</button>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs');
        let refH=0, startX=0, peakSway=0, maxXF=0, fCount=0;

        function copyData() {{
            const data = `[CALIBRATED_SWING_DATA]\\n` +
                         `Sway_Ratio: ${{document.getElementById('f_sw_p').innerText}}%\\n` +
                         `X_Factor: ${{document.getElementById('f_xf_p').innerText}}deg\\n` +
                         `Spine_Delta: ${{document.getElementById('s_sp_p').innerText}}deg`;
            navigator.clipboard.writeText(data);
            alert("보정된 수치가 복사되었습니다.");
        }}

        const poseF = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        const poseS = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        [poseF, poseS].forEach(p => p.setOptions({{modelComplexity:1, smoothLandmarks:true}}));

        poseF.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hL=lm[23], hR=lm[24], sL=lm[11], sR=lm[12];
            
            const curHipW = Math.abs(hL.x - hR.x);
            if(fCount < 20 && curHipW > 0) {{
                refH = (refH * fCount + curHipW) / (fCount + 1);
                startX = (hL.x + hR.x) / 2;
                fCount++;
            }}

            if(refH > 0) {{
                const curCX = (hL.x + hR.x) / 2;
                // [Sway 교정] 백스윙(우측 이동) 구간만 캡처하도록 이동 방향성 제한
                const curSway = ((curCX - startX) / refH) * 100;
                if(curSway > peakSway && curSway < 20) peakSway = curSway; 
                document.getElementById('f_sw_p').innerText = peakSway.toFixed(1);

                // [X-Factor 교정] 누적 합산 방지 및 절대값 각도 차이만 추출
                const sRot = Math.atan2(sR.y-sL.y, sR.x-sL.x)*180/Math.PI;
                const hRot = Math.atan2(hR.y-hL.y, hR.x-hL.x)*180/Math.PI;
                const curXF = Math.abs(sRot - hRot);
                if(curXF > maxXF && curXF < 70) maxXF = curXF; // 물리적 임계치 70도 설정
                document.getElementById('f_xf_p').innerText = maxXF.toFixed(1);
            }}
        }});
        
        // (중략: 측면 분석 로직은 기존 v57 유지)
        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vf.onplay = async () => {{ while(!vf.paused){{ await poseF.send({{image:vf}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
        vs.onplay = async () => {{ while(!vs.paused){{ await poseS.send({{image:vs}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
    </script>
    """

# [3] UI 및 리포트 섹션 (정의 가이드 포함)
f_file = st.sidebar.file_uploader("정면 영상", type=['mp4', 'mov'])
s_file = st.sidebar.file_uploader("측면 영상", type=['mp4', 'mov'])

if f_file and s_file:
    components.html(get_calibrated_engine(base64.b64encode(f_file.read()).decode(), base64.b64encode(s_file.read()).decode()), height=600)

st.divider()
st.header("🔬 기술 역학 데이터 통합 리포트")
in_text = st.text_area("보정된 데이터를 붙여넣으세요.")

if st.button("🚀 정밀 분석 시작") and model:
    prompt = f"""
    골프 역학 전문가로서 다음 정의를 바탕으로 데이터를 분석하십시오.
    1. Sway Ratio: 백스윙 중 골반 중심의 최대 우측 이동 비율 (정상: 0-15%).
    2. X-Factor: 상체와 하체의 순간 최대 회전각 차이 (정상: 40-60도).
    
    데이터: {in_text}
    
    위 수치가 시사하는 물리적 결함과 교정 방향을 기술하십시오. (개인적 언급 제외)
    """
    st.write(model.generate_content(prompt).text)
