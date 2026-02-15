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

st.set_page_config(layout="wide", page_title="GDR AI Pro v41")
st.title("⛳ GDR AI Pro: 정면/측면 통합 및 자동화 엔진 v41.0")

# [2] 정밀 역학 연산 엔진 (자동 데이터 복사 기능 포함)
def get_auto_capture_engine(v_b64, label):
    return f"""
    <div style="width:100%; background:#000; border-radius:12px; overflow:hidden; position:relative; border: 2px solid #333;">
        <video id="v_{label}" controls playsinline style="width:100%; display:block; aspect-ratio:9/16;"></video>
        <canvas id="c_{label}" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
        <div id="stats_{label}" style="position:absolute; top:10px; right:10px; background:rgba(0,0,0,0.85); color:#0f0; padding:12px; border-radius:8px; font-family:monospace; border:1px solid #0f0; font-size:11px; z-index:1000; line-height:1.4;">
            <b style="color:#fff;">[{label} DATA]</b><br>
            Δ Spine: <span id="s_{label}">0.0</span>°<br>
            Sway/X: <span id="sw_{label}">0.0</span><br>
            Speed/K: <span id="sp_{label}">0.0</span>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const v=document.getElementById('v_{label}'), c=document.getElementById('c_{label}'), ctx=c.getContext('2d');
        const sD=document.getElementById('s_{label}'), swD=document.getElementById('sw_{label}'), spD=document.getElementById('sp_{label}');
        
        let minS=180, maxS=0, startX=0, lastWristPos=null, lastTime=0, maxWristSpeed=0, angleHistory=[];

        const pose=new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:1, smoothLandmarks:true}});
        
        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            c.width=v.videoWidth; c.height=v.videoHeight;
            ctx.clearRect(0,0,c.width,c.height);
            const lm = r.poseLandmarks;
            const now = performance.now();

            // 역학 연산 (v40 로직 계승)
            const sh_c = {{x:(lm[11].x+lm[12].x)/2, y:(lm[11].y+lm[12].y)/2}};
            const h_c = {{x:(lm[23].x+lm[24].x)/2, y:(lm[23].y+lm[24].y)/2}};
            const curA = Math.abs(Math.atan2(h_c.y-sh_c.y, h_c.x-sh_c.x)*180/Math.PI);
            angleHistory.push(curA); if(angleHistory.length>3) angleHistory.shift();
            const fA = angleHistory.reduce((a,b)=>a+b)/angleHistory.length;
            if(fA<minS) minS=fA; if(fA>maxS) maxS=fA;
            sD.innerText = (maxS-minS).toFixed(1);

            // 라벨별 맞춤 추출
            if("{label}" === "FRONT") {{
                if(startX===0) startX = h_c.x;
                swD.innerText = (Math.abs(h_c.x - startX) * c.width).toFixed(1); // Sway
                const shRot = Math.atan2(lm[12].y-lm[11].y, lm[12].x-lm[11].x)*180/Math.PI;
                const hRot = Math.atan2(lm[24].y-lm[23].y, lm[24].x-lm[23].x)*180/Math.PI;
                spD.innerText = Math.abs(shRot - hRot).toFixed(1); // X-Factor
            }} else {{
                spD.innerText = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI).toFixed(1); // Knee
            }}

            ctx.strokeStyle = '#00FF00'; ctx.lineWidth = 3;
            ctx.beginPath(); ctx.moveTo(sh_c.x*c.width, sh_c.y*c.height); ctx.lineTo(h_c.x*c.width, h_c.y*c.height); ctx.stroke();
        }});
        
        const blob = new Blob([Uint8Array.from(atob("{v_b64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}});
        v.src = URL.createObjectURL(blob);
        v.onplay = async () => {{ while(!v.paused && !v.ended){{ await pose.send({{image:v}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
    </script>
    """

# [3] UI 레이아웃 및 업로더
col_u1, col_u2 = st.columns(2)
f_front = col_u1.file_uploader("정면 영상 (Sway/X-Factor 분석)", type=['mp4', 'mov'])
f_side = col_u2.file_uploader("측면 영상 (Spine/Knee 분석)", type=['mp4', 'mov'])

if f_front or f_side:
    v_col1, v_col2 = st.columns(2)
    if f_front:
        with v_col1:
            st.subheader("📸 Front Analysis")
            v_b64_f = base64.b64encode(f_front.read()).decode()
            components.html(get_auto_capture_engine(v_b64_f, "FRONT"), height=650)
    if f_side:
        with v_col2:
            st.subheader("📸 Side Analysis")
            v_b64_s = base64.b64encode(f_side.read()).decode()
            components.html(get_auto_capture_engine(v_b64_s, "SIDE"), height=650)

    st.divider()

    # [4] 통합 데이터 입력 세션 (사용자 편의성 강화)
    st.header("🔬 다각도 역학 데이터 통합 입력")
    st.info("영상 우측 상단의 실시간 수치를 아래에 입력하면 Gemini가 통합 분석을 수행합니다.")
    
    # 정면 데이터와 측면 데이터를 명확히 분리하여 입력창 구성
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("**[FRONT]**")
        f_sway = st.number_input("Sway (px)", min_value=0.0, step=1.0)
        f_xfactor = st.number_input("X-Factor (Deg)", min_value=0.0, step=0.1)
    with c2:
        st.markdown("**[SIDE]**")
        s_spine = st.number_input("Δ Spine (Deg)", min_value=0.0, step=0.1)
        s_knee = st.number_input("Knee Angle (Deg)", min_value=0.0, step=0.1)
    
    with c3:
        st.markdown("**[PERFORMANCE]**")
        p_speed = st.number_input("Wrist Speed (m/s)", min_value=0.0, step=0.1)

    # [5] 통합 분석 리포트 생성
    if st.button("🚀 정면/측면 통합 역학 진단 시작") and model:
        with st.spinner("Gemini가 두 시점의 데이터를 동기화하여 분석 중입니다..."):
            prompt = f"""
            운동역학 전문가로서 다음 정면/측면 통합 데이터를 정밀 진단하십시오.
            
            [정면 데이터] 골반 스웨이: {f_sway}px, 상하체 분리(X-Factor): {f_xfactor}°
            [측면 데이터] 척추각 편차: {s_spine}°, 무릎 유연성: {s_knee}°
            [성능 데이터] 최대 손목 속도: {p_speed}m/s
            
            분석 가이드라인:
            1. 정면의 스웨이가 측면의 척추각 유지에 어떤 부정적 영향을 주는지 물리적으로 설명하십시오.
            2. X-Factor 각도 대비 손목 속도의 효율성을 평가하여 에너지 손실 구간을 찾아내십시오.
            3. 임팩트 순간의 정타율(Smash Factor)을 높이기 위한 하체 고정 전략을 제시하십시오.
            
            기술적 용어를 사용하여 매우 전문적이고 냉철하게 분석하십시오.
            """
            response = model.generate_content(prompt)
            st.markdown("### 🤖 통합 데이터 진단 결과")
            st.write(response.text)
