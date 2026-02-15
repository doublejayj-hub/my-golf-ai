import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import base64

# [1] Gemini 모델 자가 진단 및 할당
def initialize_gemini():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for name in ['models/gemini-1.5-flash', 'models/gemini-pro']:
            if name in available_models: return genai.GenerativeModel(name)
        return genai.GenerativeModel(available_models[0]) if available_models else None
    except: return None

model = initialize_gemini()

st.set_page_config(layout="wide", page_title="GDR AI Engine v44")
st.title("⛳ GDR AI Pro: 객관적 지표 정규화 및 데이터 정의 가이드 v44.0")

# [2] 정규화 엔진 (Sway를 픽셀 대신 골반 너비 대비 비율로 계산)
def get_normalized_engine(v_b64, label):
    return f"""
    <div style="width:100%; background:#000; border-radius:12px; overflow:hidden; position:relative; border: 2px solid #333;">
        <video id="v" controls playsinline style="width:100%; display:block; aspect-ratio:9/16;"></video>
        <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
        <div id="stats" style="position:absolute; top:10px; right:10px; background:rgba(0,0,0,0.85); color:#0f0; padding:15px; border-radius:8px; font-family:monospace; border:1px solid #0f0; font-size:12px; z-index:1000;">
            <b>[{label} DATA]</b><br>
            Δ Spine: <span id="s_v">0.0</span>°<br>
            Sway Ratio: <span id="sw_v">0.0</span>%<br>
            X-Factor: <span id="x_v">0.0</span>°<br>
            Knee: <span id="k_v">0.0</span>°
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const v=document.getElementById('v'), c=document.getElementById('c'), ctx=c.getContext('2d');
        const sD=document.getElementById('s_v'), swD=document.getElementById('sw_v'), xD=document.getElementById('x_v'), kD=document.getElementById('k_v');
        let minS=180, maxS=0, startX=0, angleHistory=[];

        const pose=new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:1, smoothLandmarks:true}});
        
        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            c.width=v.videoWidth; c.height=v.videoHeight;
            ctx.clearRect(0,0,c.width,c.height);
            const lm = r.poseLandmarks;

            const h_l = lm[23], h_r = lm[24];
            const hipWidth = Math.sqrt(Math.pow(h_l.x-h_r.x, 2) + Math.pow(h_l.y-h_r.y, 2));
            const h_c = {{x:(h_l.x+h_r.x)/2, y:(h_l.y+h_r.y)/2}};
            const sh_c = {{x:(lm[11].x+lm[12].x)/2, y:(lm[11].y+lm[12].y)/2}};

            // 1. Sway Ratio (골반 너비 대비 이동 비율)
            if(startX===0) startX = h_c.x;
            const swayPx = Math.abs(h_c.x - startX);
            swD.innerText = ((swayPx / hipWidth) * 100).toFixed(1);

            // 2. Δ Spine
            const curA = Math.abs(Math.atan2(h_c.y-sh_c.y, h_c.x-sh_c.x)*180/Math.PI);
            angleHistory.push(curA); if(angleHistory.length>3) angleHistory.shift();
            const fA = angleHistory.reduce((a,b)=>a+b)/angleHistory.length;
            if(fA<minS) minS=fA; if(fA>maxS) maxS=fA;
            sD.innerText = (maxS-minS).toFixed(1);

            // 3. X-Factor & Knee
            const shRot = Math.atan2(lm[12].y-lm[11].y, lm[12].x-lm[11].x)*180/Math.PI;
            const hRot = Math.atan2(lm[24].y-lm[23].y, lm[24].x-lm[23].x)*180/Math.PI;
            xD.innerText = Math.abs(shRot - hRot).toFixed(1);
            kD.innerText = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI).toFixed(1);

            ctx.strokeStyle = '#00FF00'; ctx.lineWidth = 3;
            ctx.beginPath(); ctx.moveTo(sh_c.x*c.width, sh_c.y*c.height); ctx.lineTo(h_c.x*c.width, h_c.y*c.height); ctx.stroke();
        }});
        
        const blob = new Blob([Uint8Array.from(atob("{v_b64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}});
        v.src = URL.createObjectURL(blob);
        v.onplay = async () => {{ while(!v.paused && !v.ended){{ await pose.send({{image:v}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
    </script>
    """

# [3] 파일 업로드 및 데이터 입력
f_front = st.sidebar.file_uploader("정면 영상", type=['mp4', 'mov'])
f_side = st.sidebar.file_uploader("측면 영상", type=['mp4', 'mov'])

col_v1, col_v2 = st.columns(2)
if f_front:
    with col_v1:
        st.subheader("📸 Front Analysis")
        components.html(get_normalized_engine(base64.b64encode(f_front.read()).decode(), "FRONT"), height=650)
if f_side:
    with col_v2:
        st.subheader("📸 Side Analysis")
        components.html(get_normalized_engine(base64.b64encode(f_side.read()).decode(), "SIDE"), height=650)

st.divider()

# [4] 데이터 가이드 및 리포트 섹션
st.header("📊 데이터 정의 및 통합 분석")
with st.expander("ℹ️ 각 지표의 기술적 정의 (Standard Guide)"):
    st.markdown("""
    * **Δ Spine (Deg)**: 척추축의 안정도. (정상: 0~4° / 5° 이상 시 얼리 익스텐션 주의)
    * **Sway Ratio (%)**: 골반 너비 대비 좌우 이동 비율. (정상: 0~15% / 20% 이상 시 축 무너짐)
    * **X-Factor (Deg)**: 상하체 꼬임각. (프로 평균: 45°~55°)
    * **Knee Angle (Deg)**: 하체 고정각. (임팩트 시 변화폭 최소화 권장)
    """)

c1, c2, c3 = st.columns(3)
in_sway = c1.number_input("Sway Ratio (%)", min_value=0.0, step=0.1)
in_x = c1.number_input("X-Factor (Deg)", min_value=0.0, step=0.1)
in_spine = c2.number_input("Δ Spine (Deg)", min_value=0.0, step=0.1)
in_knee = c2.number_input("Knee Angle (Deg)", min_value=0.0, step=0.1)
in_speed = c3.number_input("Wrist Speed (m/s)", min_value=0.0, step=0.1)

if st.button("🚀 종합 데이터 리포트 생성") and model:
    with st.spinner("Gemini가 정규화된 데이터를 바탕으로 분석 중입니다..."):
        prompt = f"""
        당신은 물리 데이터 기반 골프 역학 전문가입니다.
        제시된 지표는 픽셀이 아닌 신체 너비 대비 비율(%) 및 각도로 정규화된 객관적 수치입니다.
        
        [데이터 요약]
        - Sway Ratio: {in_sway}% (골반 너비 대비 이동량)
        - X-Factor: {in_x}°
        - Δ Spine: {in_spine}°
        - Knee Angle: {in_knee}°
        - Wrist Speed: {in_speed}m/s
        
        1. Sway Ratio가 {in_sway}%인 점을 고려할 때, 지면 반력 효율성을 진단하십시오.
        2. 상기 5개 데이터의 인과관계를 물리적으로 분석하십시오. (예: Sway가 크면 X-Factor에 미치는 영향 등)
        3. 철저히 기술적 관점에서 교정 방향을 서술하십시오.
        """
        response = model.generate_content(prompt)
        st.info("🤖 Gemini 전문 분석 결과")
        st.write(response.text)
