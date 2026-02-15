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

st.set_page_config(layout="wide", page_title="GDR AI Engine v49")
st.title("⛳ GDR AI Pro: 전방위 역학 분석 v49.0")

# [2] 분석 모드 선택 및 엔진 설정
view_mode = st.sidebar.radio("분석 시점 선택", ("정면 (Front View)", "측면 (Side View)"))

def get_expert_engine(v_b64, mode):
    label = "FRONT" if "정면" in mode else "SIDE"
    return f"""
    <div style="width:100%; background:#000; border-radius:12px; overflow:hidden; position:relative; border: 2px solid #333;">
        <video id="v" controls playsinline style="width:100%; display:block; aspect-ratio:9/16;"></video>
        <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
        <div id="stats" style="position:absolute; top:10px; right:10px; background:rgba(0,0,0,0.85); color:#0f0; padding:15px; border-radius:8px; font-family:monospace; border:1px solid #0f0; z-index:1000; font-size:12px;">
            <b>[{label} DATA]</b><br>
            Δ Spine: <span id="s_v">0.0</span>°<br>
            Sway Ratio: <span id="sw_v">0.0</span>%<br>
            X-Factor: <span id="x_v">0.0</span>°<br>
            Knee Angle: <span id="k_v">0.0</span>°
        </div>
        <button onclick="copyData()" style="position:absolute; bottom:15px; right:15px; z-index:1001; background:#0f0; color:#000; border:none; padding:10px 15px; border-radius:5px; cursor:pointer; font-weight:bold;">📋 수치 복사</button>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const v=document.getElementById('v'), c=document.getElementById('c'), ctx=c.getContext('2d');
        const sD=document.getElementById('s_v'), swD=document.getElementById('sw_v'), xD=document.getElementById('x_v'), kD=document.getElementById('k_v');
        let minS=180, maxS=0, startX=0, angleHistory=[];

        function copyData() {{
            const data = `[${{label}}] Sway Ratio: ${{swD.innerText}}%, Spine: ${{sD.innerText}}°, X-Factor: ${{xD.innerText}}°, Knee: ${{kD.innerText}}°`;
            navigator.clipboard.writeText(data);
            alert(`${{label}} 데이터가 복사되었습니다!`);
        }}

        const pose=new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:1, smoothLandmarks:true}});
        
        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            c.width=v.videoWidth; c.height=v.videoHeight;
            ctx.clearRect(0,0,c.width,c.height);
            const lm = r.poseLandmarks;
            const h_l=lm[23], h_r=lm[24], sh_l=lm[11], sh_r=lm[12];
            const hipW = Math.sqrt(Math.pow(h_l.x-h_r.x,2)+Math.pow(h_l.y-h_r.y,2));
            const h_c = {{x:(h_l.x+h_r.x)/2, y:(h_l.y+h_r.y)/2}};
            const sh_c = {{x:(sh_l.x+sh_r.x)/2, y:(sh_l.y+sh_r.y)/2}};

            // 1. Δ Spine (측면 핵심)
            const curA = Math.abs(Math.atan2(h_c.y-sh_c.y, h_c.x-sh_c.x)*180/Math.PI);
            angleHistory.push(curA); if(angleHistory.length>3) angleHistory.shift();
            const fA = angleHistory.reduce((a,b)=>a+b)/angleHistory.length;
            if(fA<minS) minS=fA; if(fA>maxS) maxS=fA;
            sD.innerText = (maxS-minS).toFixed(1);

            // 2. Sway Ratio (정면 핵심)
            if(startX===0) startX = h_c.x;
            swD.innerText = ((Math.abs(h_c.x - startX) / hipW) * 100).toFixed(1);

            // 3. X-Factor
            const shRot = Math.atan2(sh_r.y-sh_l.y, sh_r.x-sh_l.x)*180/Math.PI;
            const hRot = Math.atan2(h_r.y-h_l.y, h_r.x-h_l.x)*180/Math.PI;
            xD.innerText = Math.abs(shRot - hRot).toFixed(1);

            // 4. Knee Angle
            kD.innerText = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI).toFixed(1);

            ctx.strokeStyle = '#00FF00'; ctx.lineWidth = 4;
            ctx.beginPath(); ctx.moveTo(sh_c.x*c.width, sh_c.y*c.height); ctx.lineTo(h_c.x*c.width, h_c.y*c.height); ctx.stroke();
        }});
        
        const blob = new Blob([Uint8Array.from(atob("{v_b64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}});
        v.src = URL.createObjectURL(blob);
        v.onplay = async () => {{ while(!v.paused && !v.ended){{ await pose.send({{image:v}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
    </script>
    """

# [3] 파일 업로드
f = st.file_uploader(f"{view_mode} 영상을 업로드하세요", type=['mp4', 'mov'])
if f:
    v_b64 = base64.b64encode(f.read()).decode()
    components.html(get_expert_engine(v_b64, view_mode), height=700)

st.divider()

# [4] 제미나이 리포트 (데이터 정의 강화)
st.header("🔬 전문 역학 통합 리포트")
in_text = st.text_area("복사한 데이터를 여기에 붙여넣으세요.")

if st.button("🚀 정밀 분석 시작") and model:
    with st.spinner("서버 모델이 데이터를 물리적으로 해석 중..."):
        prompt = f"""
        당신은 물리 데이터 기반 골프 역학 전문가입니다. 다음 수치 정의를 바탕으로 분석하십시오.
        
        - Δ Spine: 척추축 안정도 지표. 측면 뷰에서 척추각이 얼마나 들리는지(Early Extension)를 평가합니다.
        - Knee Angle: 임팩트 시 하체 고정력을 평가하는 지표입니다.
        - Sway Ratio: 골반 너비 대비 수평 이동 비율입니다.
        
        [입력 데이터]
        {in_text}
        
        위 시점(View)의 특성을 고려하여 물리적 결함을 진단하고 교정 방안을 기술적으로 제시하십시오. 개인적 언급은 배제하십시오.
        """
        response = model.generate_content(prompt)
        st.write(response.text)
