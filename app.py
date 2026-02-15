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

st.set_page_config(layout="wide", page_title="GDR AI Pro v60")
st.title("⛳ GDR AI Pro: 변곡점 포착 및 피크 홀딩 엔진 v60.0")

# [2] 정점 포착 최적화 엔진
def get_peak_locked_engine(f_v64, s_v64):
    return f"""
    <div style="display: flex; gap: 15px; background: #000; padding: 15px; border-radius: 12px;">
        <div style="flex: 1; position: relative;">
            <h4 style="color:#0f0; text-align:center;">FRONT (Capture Peak)</h4>
            <video id="vf" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div id="stats_f" style="margin-top:10px; background:rgba(0,255,0,0.1); color:#0f0; padding:12px; border-radius:8px; font-family:monospace; border:1px solid #0f0;">
                Max Sway: <span id="f_sw_max">0.0</span>% | Max X-Factor: <span id="f_xf_max">0.0</span>°
            </div>
        </div>
        <div style="flex: 1; position: relative;">
            <h4 style="color:#0f0; text-align:center;">SIDE (Capture Peak)</h4>
            <video id="vs" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div id="stats_s" style="margin-top:10px; background:rgba(0,255,0,0.1); color:#0f0; padding:12px; border-radius:8px; font-family:monospace; border:1px solid #0f0;">
                Max Δ Spine: <span id="s_sp_max">0.0</span>° | Knee: <span id="s_kn">0.0</span>°
            </div>
        </div>
    </div>
    <div style="text-align: center; margin-top: 20px;">
        <button onclick="resetAndCopy()" style="background:#0f0; color:#000; border:none; padding:12px 25px; border-radius:8px; cursor:pointer; font-weight:bold; font-size:16px;">
            📋 정점(Peak) 데이터 복사 및 리셋
        </button>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs');
        let f_refH=0, f_startX=0, f_maxSw=0, f_maxXF=0, f_cnt=0;
        let s_minS=180, s_maxS=0, s_peakSp=0;

        function resetAndCopy() {{
            const data = `[PEAK_ANALYSIS]\\n` +
                         `FRONT_MaxSway: ${{document.getElementById('f_sw_max').innerText}}%\\n` +
                         `FRONT_MaxXFactor: ${{document.getElementById('f_xf_max').innerText}}deg\\n` +
                         `SIDE_MaxSpineDelta: ${{document.getElementById('s_sp_max').innerText}}deg`;
            navigator.clipboard.writeText(data);
            alert("영상 내 최고 정점 수치가 복사되었습니다.");
            // 리셋하여 새로운 스윙 측정 준비
            f_maxSw=0; f_maxXF=0; s_peakSp=0; s_minS=180; s_maxS=0;
        }}

        const poseF = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        const poseS = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        [poseF, poseS].forEach(p => p.setOptions({{modelComplexity:1, smoothLandmarks:true}}));

        poseF.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hL=lm[23], hR=lm[24], sL=lm[11], sR=lm[12];
            
            if(f_cnt < 15) {{
                f_refH = (f_refH * f_cnt + Math.abs(hL.x - hR.x)) / (f_cnt + 1);
                f_startX = (hL.x + hR.x) / 2;
                f_cnt++;
                return;
            }}

            // Peak Sway 포착 (최대치만 갱신)
            const curSw = (( (hL.x + hR.x)/2 - f_startX) / f_refH) * 100;
            if(curSw > f_maxSw && curSw < 25) f_maxSw = curSw;
            document.getElementById('f_sw_max').innerText = f_maxSw.toFixed(1);

            // Peak X-Factor 포착 (누적 각도 아닌 절대 차이의 정점)
            const curXF = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
            if(curXF > f_maxXF && curXF < 75) f_maxXF = curXF;
            document.getElementById('f_xf_max').innerText = f_maxXF.toFixed(1);
        }});

        poseS.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hC = {{x:(lm[23].x+lm[24].x)/2, y:(lm[23].y+lm[24].y)/2}};
            const sC = {{x:(lm[11].x+lm[12].x)/2, y:(lm[11].y+lm[12].y)/2}};
            const curS = Math.abs(Math.atan2(hC.y-sC.y, hC.x-sC.x)*180/Math.PI);
            
            if(curS > 40 && curS < 140) {{
                if(curS < s_minS) s_minS = curS;
                if(curS > s_maxS) s_maxS = curS;
                if((s_maxS - s_minS) > s_peakSp) s_peakSp = s_maxS - s_minS;
                document.getElementById('s_sp_max').innerText = s_peakSp.toFixed(1);
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
with c1: f_f = st.file_uploader("Front 영상 (Front)", type=['mp4', 'mov'])
with c2: s_f = st.file_uploader("Side 영상 (Side)", type=['mp4', 'mov'])

if f_f and s_f:
    f_b64 = base64.b64encode(f_f.read()).decode()
    s_b64 = base64.b64encode(s_f.read()).decode()
    components.html(get_peak_locked_engine(f_b64, s_b64), height=600)

st.divider()
st.header("🔬 정밀 역학 정점 분석 리포트")
in_text = st.text_area("복사된 'Peak' 데이터를 여기에 붙여넣으세요.")

if st.button("🚀 정점 기반 분석 시작") and model:
    prompt = f"""
    당신은 운동역학 전문가입니다. 다음은 스윙 중 가장 수치가 높았던 '정점(Peak)'에서의 데이터입니다.
    {in_text}
    
    물리적 관점에서 축 유지와 비거리 잠재력을 진단하십시오. 개인적 언급은 배제하십시오.
    """
    st.write(model.generate_content(prompt).text)
