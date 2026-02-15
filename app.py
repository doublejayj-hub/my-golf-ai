import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import base64

# [1] 모델 자동 탐색 및 강제 할당 (404 오류 방지)
def get_working_model():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # v1beta 환경에서도 인식 가능한 경로 탐색
        for target in ['models/gemini-1.5-flash', 'models/gemini-pro', 'gemini-1.5-flash']:
            if target in models: return genai.GenerativeModel(target)
        return genai.GenerativeModel(models[0]) if models else None
    except: return None

model = get_working_model()

st.set_page_config(layout="wide", page_title="GDR AI Engine v48")
st.title("⛳ GDR AI Pro: 정면 역학 정밀 분석 v48.0")

# [2] 정면 전용 역학 엔진 (X-Factor 연산 강화)
def get_front_engine(v_b64):
    return f"""
    <div style="width:100%; background:#000; border-radius:12px; overflow:hidden; position:relative; border: 2px solid #333;">
        <video id="v" controls playsinline style="width:100%; display:block; aspect-ratio:9/16; background:#000;"></video>
        <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
        <div id="stats" style="position:absolute; top:10px; right:10px; background:rgba(0,0,0,0.85); color:#0f0; padding:15px; border-radius:8px; font-family:monospace; border:1px solid #0f0; z-index:1000;">
            <b style="color:#fff;">[FRONT VIEW DATA]</b><br>
            Sway Ratio: <span id="sw_v">0.0</span>%<br>
            X-Factor: <span id="x_v">0.0</span>°<br>
            Shoulder Tilt: <span id="t_v">0.0</span>°
        </div>
        <button onclick="copyFrontData()" style="position:absolute; bottom:15px; right:15px; z-index:1001; background:#0f0; color:#000; border:none; padding:10px 15px; border-radius:5px; cursor:pointer; font-weight:bold;">📋 수치 복사</button>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const v=document.getElementById('v'), c=document.getElementById('c'), ctx=c.getContext('2d');
        const swD=document.getElementById('sw_v'), xD=document.getElementById('x_v'), tD=document.getElementById('t_v');
        let startX=0, maxXF=0;

        function copyFrontData() {{
            const data = `Sway Ratio: ${{swD.innerText}}%, X-Factor: ${{xD.innerText}}°, Shoulder Tilt: ${{tD.innerText}}°`;
            navigator.clipboard.writeText(data);
            alert("정면 분석 데이터가 복사되었습니다!");
        }}

        const pose=new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:1, smoothLandmarks:true}});
        
        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            c.width=v.videoWidth; c.height=v.videoHeight;
            ctx.clearRect(0,0,c.width,c.height);
            const lm = r.poseLandmarks;

            // 골반 너비 기준 정규화 (Sway Ratio)
            const h_l = lm[23], h_r = lm[24];
            const hipW = Math.sqrt(Math.pow(h_l.x-h_r.x,2)+Math.pow(h_l.y-h_r.y,2));
            const h_c = {{x:(h_l.x+h_r.x)/2, y:(h_l.y+h_r.y)/2}};
            if(startX===0) startX = h_c.x;
            swD.innerText = ((Math.abs(h_c.x - startX) / hipW) * 100).toFixed(1);

            // X-Factor (상하체 회전 분리)
            const shRot = Math.atan2(lm[12].y-lm[11].y, lm[12].x-lm[11].x)*180/Math.PI;
            const hRot = Math.atan2(h_r.y-h_l.y, h_r.x-h_l.x)*180/Math.PI;
            const curXF = Math.abs(shRot - hRot);
            if(curXF > maxXF) maxXF = curXF;
            xD.innerText = maxXF.toFixed(1);

            // Shoulder Tilt
            tD.innerText = Math.abs(shRot).toFixed(1);

            ctx.strokeStyle = '#00FF00'; ctx.lineWidth = 4;
            ctx.beginPath(); ctx.moveTo(lm[11].x*c.width, lm[11].y*c.height); ctx.lineTo(lm[12].x*c.width, lm[12].y*c.height); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(lm[23].x*c.width, lm[23].y*c.height); ctx.lineTo(lm[24].x*c.width, lm[24].y*c.height); ctx.stroke();
        }});
        
        const blob = new Blob([Uint8Array.from(atob("{v_b64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}});
        v.src = URL.createObjectURL(blob);
        v.onplay = async () => {{ while(!v.paused && !v.ended){{ await pose.send({{image:v}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
    </script>
    """

# [3] 파일 업로드 및 분석기
f_input = st.file_uploader("정면 스윙 영상을 업로드하세요", type=['mp4', 'mov'])
if f_input:
    v_b64 = base64.b64encode(f_input.read()).decode()
    components.html(get_front_engine(v_b64), height=700)

st.divider()

# [4] 데이터 기술 통합 리포트 (X-Factor 정의 강조)
st.header("🔬 정면 역학 통합 리포트")
in_text = st.text_area("복사한 데이터를 여기에 붙여넣으세요.")

if st.button("🚀 제미나이 리포트 생성") and model:
    with st.spinner("전문 역학 데이터 해석 중..."):
        prompt = f"""
        당신은 물리 데이터 기반 골프 역학 전문가입니다. 다음 정의를 바탕으로 분석하십시오.
        
        1. X-Factor: 어깨 회전선과 골반 회전선의 각도 차이로, 상하체 분리 및 꼬임 에너지를 의미합니다.
        2. Sway Ratio: 골반 너비 대비 수평 이동 비율(%)입니다.
        
        [사용자 정면 데이터]
        {in_text}
        
        Sway Ratio와 X-Factor의 상관관계를 통해 회전축의 안정성과 비거리 잠재력을 물리적 관점에서 진단하고 개선책을 제시하십시오. 
        개인적 언급 없이 기술적 분석만 수행하십시오.
        """
        try:
            response = model.generate_content(prompt)
            st.success(f"분석 완료 (사용 모델: {model.model_name})")
            st.write(response.text)
        except Exception as e:
            st.error(f"리포트 생성 실패: {e}")
