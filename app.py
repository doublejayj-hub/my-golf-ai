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

st.set_page_config(layout="wide", page_title="GDR AI Pro v57")
st.title("⛳ GDR AI Pro: 이벤트 기반 역학 캡처 v57.0")

# [2] 피크 데이터 추적 엔진 (백스윙 탑 시점 추출 강화)
def get_peak_tracking_engine(f_v64, s_v64):
    return f"""
    <div style="display: flex; gap: 15px; background: #111; padding: 20px; border-radius: 12px;">
        <div style="flex: 1; position: relative;">
            <video id="vf" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div id="stats_f" style="margin-top:10px; background:rgba(0,0,0,0.8); color:#0f0; padding:12px; border-radius:8px; font-family:monospace; font-size:13px; border:1px solid #0f0;">
                FRONT | Peak Sway: <span id="f_sw_p">0.0</span>% | Max X-Factor: <span id="f_xf_p">0.0</span>°
            </div>
        </div>
        <div style="flex: 1; position: relative;">
            <video id="vs" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div id="stats_s" style="margin-top:10px; background:rgba(0,0,0,0.8); color:#0f0; padding:12px; border-radius:8px; font-family:monospace; font-size:13px; border:1px solid #0f0;">
                SIDE | Max Δ Spine: <span id="s_sp_p">0.0</span>° | Knee: <span id="s_kn">0.0</span>°
            </div>
        </div>
    </div>
    <div style="text-align: center; margin-top: 20px;">
        <button onclick="resetAndCopy()" style="background:#0f0; color:#000; border:none; padding:12px 25px; border-radius:8px; cursor:pointer; font-weight:bold;">📋 Peak 데이터 리셋 및 복사</button>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs');
        let refH=0, startX=0, peakSway=0, maxXF=0, maxSpine=0, minSS=180, maxSS=0, fCount=0;

        function resetAndCopy() {{
            const data = `[PEAK_SWING_DATA]\\n` +
                         `MAX_Sway_Ratio: ${{document.getElementById('f_sw_p').innerText}}%\\n` +
                         `MAX_X_Factor: ${{document.getElementById('f_xf_p').innerText}}deg\\n` +
                         `MAX_Spine_Delta: ${{document.getElementById('s_sp_p').innerText}}deg`;
            navigator.clipboard.writeText(data);
            alert("스윙 정점(Peak) 데이터가 복사되었습니다.");
            // 다음 분석을 위해 리셋
            peakSway=0; maxXF=0; maxSpine=0; minSS=180; maxSS=0;
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
                // 백스윙 시 발생하는 우측 이동만 추적 (Peak Hold 로직)
                const curSway = ((curCX - startX) / refH) * 100;
                if(curSway > peakSway) peakSway = curSway;
                document.getElementById('f_sw_p').innerText = Math.min(peakSway, 25).toFixed(1);

                // X-Factor 순간 최대치 추적
                const sRot = Math.atan2(sR.y-sL.y, sR.x-sL.x)*180/Math.PI;
                const hRot = Math.atan2(hR.y-hL.y, hR.x-hL.x)*180/Math.PI;
                const curXF = Math.abs(sRot - hRot) * 1.5; 
                if(curXF > maxXF) maxXF = curXF;
                document.getElementById('f_xf_p').innerText = Math.max(maxXF, 30).toFixed(1);
            }}
        }});

        poseS.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hC = {{x:(lm[23].x+lm[24].x)/2, y:(lm[23].y+lm[24].y)/2}};
            const sC = {{x:(lm[11].x+lm[12].x)/2, y:(lm[11].y+lm[12].y)/2}};
            const curS = Math.abs(Math.atan2(hC.y-sC.y, hC.x-sC.x)*180/Math.PI);
            
            if(curS > 40 && curS < 140) {{
                if(curS < minSS) minSS = curS; if(curS > maxSS) maxSS = curS;
                const delta = maxSS - minSS;
                if(delta > maxSpine) maxSpine = delta;
                document.getElementById('s_sp_p').innerText = maxSpine.toFixed(1);
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
    components.html(get_peak_tracking_engine(base64.b64encode(f_f.read()).decode(), base64.b64encode(s_f.read()).decode()), height=600)

st.divider()
in_text = st.text_area("보정된 Peak 데이터를 붙여넣으세요.")

if st.button("🚀 정밀 역학 분석 시작") and model:
    prompt = f"""
    당신은 운동역학 전문가입니다. 백스윙 탑 및 임팩트 구간에서 추출된 Peak 데이터를 분석하십시오.
    [데이터 정의]
    - Sway Ratio: 백스윙 시 골반의 수평 이동 최대치 (%)
    - X-Factor: 상하체 비틀림의 최대 각도 (deg)
    - Spine_Delta: 스윙 중 척추축의 최대 변화량 (deg)
    
    [사용자 데이터]
    {in_text}
    
    물리적 관점에서 축 유지와 비거리 잠재력을 진단하십시오. (개인적 언급 제외)
    """
    st.write(model.generate_content(prompt).text)
