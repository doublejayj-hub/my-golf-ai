import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import base64

# [1] 모델 자동 탐색 및 할당
def get_working_model():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for target in ['models/gemini-1.5-flash', 'models/gemini-pro']:
            if target in models: return genai.GenerativeModel(target)
        return genai.GenerativeModel(models[0]) if models else None
    except: return None

model = get_working_model()

st.set_page_config(layout="wide", page_title="GDR AI Engine v53")
st.title("⛳ GDR AI Pro: 정면/측면 통합 역학 분석 v53.0")

# [2] 통합 분석 엔진 HTML (정면/측면 동시 처리 및 통합 복사)
def get_dual_engine(f_v64, s_v64):
    return f"""
    <div style="display: flex; gap: 20px; background: #111; padding: 20px; border-radius: 15px;">
        <div style="flex: 1; position: relative;">
            <h3 style="color: #0f0; text-align: center;">FRONT VIEW</h3>
            <video id="vf" controls playsinline style="width: 100%; border-radius: 10px;"></video>
            <canvas id="cf" style="position: absolute; top: 40px; left: 0; width: 100%; height: 85%; pointer-events: none;"></canvas>
            <div id="stats_f" style="margin-top: 10px; background: rgba(0,255,0,0.1); color: #0f0; padding: 10px; border-radius: 5px; font-family: monospace;">
                Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°
            </div>
        </div>
        
        <div style="flex: 1; position: relative;">
            <h3 style="color: #0f0; text-align: center;">SIDE VIEW</h3>
            <video id="vs" controls playsinline style="width: 100%; border-radius: 10px;"></video>
            <canvas id="cs" style="position: absolute; top: 40px; left: 0; width: 100%; height: 85%; pointer-events: none;"></canvas>
            <div id="stats_s" style="margin-top: 10px; background: rgba(0,255,0,0.1); color: #0f0; padding: 10px; border-radius: 5px; font-family: monospace;">
                Δ Spine: <span id="s_sp">0.0</span>° | Knee: <span id="s_kn">0.0</span>°
            </div>
        </div>
    </div>
    
    <div style="text-align: center; margin-top: 20px;">
        <button onclick="copyDualData()" style="background: #0f0; color: #000; border: none; padding: 15px 30px; border-radius: 10px; cursor: pointer; font-weight: bold; font-size: 16px;">
            📋 정면/측면 통합 데이터 복사
        </button>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), cf=document.getElementById('cf'), ctxf=cf.getContext('2d');
        const vs=document.getElementById('vs'), cs=document.getElementById('cs'), ctxs=cs.getContext('2d');
        
        let startX_f=0, minS_s=180, maxS_s=0;

        function copyDualData() {{
            const f_sw = document.getElementById('f_sw').innerText;
            const f_xf = document.getElementById('f_xf').innerText;
            const s_sp = document.getElementById('s_sp').innerText;
            const s_kn = document.getElementById('s_kn').innerText;
            
            const dataStr = `[FRONT_DATA]\\nSway: ${{f_sw}}%\\nX-Factor: ${{f_xf}}deg\\n\\n[SIDE_DATA]\\nSpine_Delta: ${{s_sp}}deg\\nKnee_Angle: ${{s_kn}}deg`;
            navigator.clipboard.writeText(dataStr);
            alert("통합 데이터가 복사되었습니다. 아래 리포트 생성 칸에 붙여넣으세요.");
        }}

        const poseF = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        const poseS = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        [poseF, poseS].forEach(p => p.setOptions({{modelComplexity:1, smoothLandmarks:true}}));

        // 정면 처리 로직
        poseF.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            cf.width=vf.videoWidth; cf.height=vf.videoHeight;
            const lm = r.poseLandmarks;
            const h_l=lm[23], h_r=lm[24], sh_l=lm[11], sh_r=lm[12];
            if(startX_f===0) startX_f = (h_l.x+h_r.x)/2;
            document.getElementById('f_sw').innerText = ((Math.abs((h_l.x+h_r.x)/2 - startX_f) / Math.abs(h_l.x-h_r.x)) * 100).toFixed(1);
            document.getElementById('f_xf').innerText = Math.abs((Math.atan2(sh_r.y-sh_l.y, sh_r.x-sh_l.x) - Math.atan2(h_r.y-h_l.y, h_r.x-h_l.x))*180/Math.PI).toFixed(1);
        }});

        // 측면 처리 로직
        poseS.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            cs.width=vs.videoWidth; cs.height=vs.videoHeight;
            const lm = r.poseLandmarks;
            const curA = Math.abs(Math.atan2((lm[23].y+lm[24].y)/2 - (lm[11].y+lm[12].y)/2, (lm[23].x+lm[24].x)/2 - (lm[11].x+lm[12].x)/2)*180/Math.PI);
            if(curA<minS_s) minS_s=curA; if(curA>maxS_s) maxS_s=curA;
            document.getElementById('s_sp').innerText = (maxS_s-minS_s).toFixed(1);
            document.getElementById('s_kn').innerText = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI).toFixed(1);
        }});

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        
        vf.onplay = async () => {{ while(!vf.paused){{ await poseF.send({{image:vf}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
        vs.onplay = async () => {{ while(!vs.paused){{ await poseS.send({{image:vs}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
    </script>
    """

# [3] 파일 업로드 (2개 섹션)
col1, col2 = st.columns(2)
with col1: f_file = st.file_uploader("정면 영상 업로드", type=['mp4', 'mov'])
with col2: s_file = st.file_uploader("측면 영상 업로드", type=['mp4', 'mov'])

if f_file and s_file:
    f_b64 = base64.b64encode(f_file.read()).decode()
    s_b64 = base64.b64encode(s_file.read()).decode()
    components.html(get_dual_engine(f_b64, s_b64), height=600)

st.divider()

# [4] 제미나이 통합 리포트
st.header("🔬 정면/측면 통합 역학 리포트")
in_text = st.text_area("통합 복사된 데이터를 여기에 붙여넣으세요.")

if st.button("🚀 전체 스윙 분석 시작") and model:
    with st.spinner("두 시점의 데이터를 교차 분석 중..."):
        prompt = f"""
        당신은 물리 데이터 기반 골프 역학 전문가입니다.
        제공된 [FRONT_DATA]와 [SIDE_DATA]를 결합하여 스윙의 입체적 결함을 진단하십시오.
        
        - X-Factor는 비거리 잠재력을, Spine_Delta는 샷의 일관성(배치기 유무)을 나타냅니다.
        - 두 데이터 사이의 역학적 인과관계를 찾아내십시오. (예: 과도한 Sway가 Spine_Delta에 주는 영향)
        
        [입력 데이터]
        {in_text}
        
        철저히 기술적 관점에서 서술하고, 개인적인 격려나 언급은 생략하십시오.
        """
        response = model.generate_content(prompt)
        st.write(response.text)
