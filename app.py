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

st.set_page_config(layout="wide", page_title="GDR AI Engine v40")
st.title("⛳ GDR AI Pro: 고급 역학 파라미터 통합 엔진 v40.0")

# [2] 정밀 역학 연산 엔진 (X-Factor 및 속도 추정 로직 포함)
def get_advanced_engine(v_b64, label):
    return f"""
    <div style="width:100%; background:#000; border-radius:12px; overflow:hidden; position:relative; border: 2px solid #333;">
        <video id="v_{label}" controls playsinline style="width:100%; display:block; aspect-ratio:9/16; background:#000;"></video>
        <canvas id="c_{label}" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
        <div id="stats_{label}" style="position:absolute; top:10px; right:10px; background:rgba(0,0,0,0.85); color:#0f0; padding:12px; border-radius:8px; font-family:monospace; border:1px solid #0f0; font-size:11px; z-index:1000; line-height:1.4;">
            <b style="color:#fff;">[{label} ADVANCED DATA]</b><br>
            Δ Spine: <span id="s_{label}">0.0</span>°<br>
            Sway: <span id="sw_{label}">0.0</span>px<br>
            X-Factor: <span id="x_{label}">0.0</span>°<br>
            Wrist Spd: <span id="sp_{label}">0.0</span>m/s<br>
            Knee: <span id="k_{label}">0.0</span>°
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const v=document.getElementById('v_{label}'), c=document.getElementById('c_{label}'), ctx=c.getContext('2d');
        const sD=document.getElementById('s_{label}'), swD=document.getElementById('sw_{label}'), xD=document.getElementById('x_{label}'), spD=document.getElementById('sp_{label}'), kD=document.getElementById('k_{label}');
        
        let minS=180, maxS=0, startX=0, lastWristPos=null, lastTime=0, maxWristSpeed=0;
        let angleHistory=[];

        const pose=new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:1, smoothLandmarks:true}});
        
        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            c.width=v.videoWidth; c.height=v.videoHeight;
            ctx.clearRect(0,0,c.width,c.height);
            const lm = r.poseLandmarks;
            const now = performance.now();

            // 1. 척추각 및 필터링
            const sh_c = {{x:(lm[11].x+lm[12].x)/2, y:(lm[11].y+lm[12].y)/2}};
            const h_c = {{x:(lm[23].x+lm[24].x)/2, y:(lm[23].y+lm[24].y)/2}};
            const curAngle = Math.abs(Math.atan2(h_c.y-sh_c.y, h_c.x-sh_c.x)*180/Math.PI);
            angleHistory.push(curAngle); if(angleHistory.length>3) angleHistory.shift();
            const fAngle = angleHistory.reduce((a,b)=>a+b)/angleHistory.length;
            if(fAngle<minS) minS=fAngle; if(fAngle>maxS) maxS=fAngle;
            sD.innerText = (maxS-minS).toFixed(1);

            // 2. X-Factor (상하체 분리 각도)
            const shRot = Math.atan2(lm[12].y-lm[11].y, lm[12].x-lm[11].x)*180/Math.PI;
            const hRot = Math.atan2(lm[24].y-lm[23].y, lm[24].x-lm[23].x)*180/Math.PI;
            xD.innerText = Math.abs(shRot - hRot).toFixed(1);

            // 3. Wrist Speed (헤드 스피드 추정 기초 데이터)
            const wrist = lm[15]; // Left Wrist
            if(lastWristPos && lastTime > 0) {{
                const dt = (now - lastTime) / 1000;
                const dist = Math.sqrt(Math.pow(wrist.x-lastWristPos.x, 2) + Math.pow(wrist.y-lastWristPos.y, 2));
                const speed = (dist * 2.0) / dt; // 2.0은 신장 대비 픽셀 보정 계수(가상)
                if(speed > maxWristSpeed) maxWristSpeed = speed;
                spD.innerText = maxWristSpeed.toFixed(1);
            }}
            lastWristPos = {{x:wrist.x, y:wrist.y}};
            lastTime = now;

            // 4. 변위(Sway) 및 무릎 각도
            if(startX===0) startX = h_c.x;
            swD.innerText = (Math.abs(h_c.x - startX) * c.width).toFixed(1);
            kD.innerText = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI).toFixed(1);

            // 시각화 (척추선 및 어깨-골반 라인)
            ctx.strokeStyle = '#00FF00'; ctx.lineWidth = 3;
            ctx.beginPath(); ctx.moveTo(lm[11].x*c.width, lm[11].y*c.height); ctx.lineTo(lm[12].x*c.width, lm[12].y*c.height); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(lm[23].x*c.width, lm[23].y*c.height); ctx.lineTo(lm[24].x*c.width, lm[24].y*c.height); ctx.stroke();
        }});
        
        const blob = new Blob([Uint8Array.from(atob("{v_b64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}});
        v.src = URL.createObjectURL(blob);
        v.onplay = async () => {{ while(!v.paused && !v.ended){{ await pose.send({{image:v}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
    </script>
    """

# [3] UI 레이아웃
col_u1, col_u2 = st.columns(2)
f_front = col_u1.file_uploader("정면 영상 (Front View)", type=['mp4', 'mov'])
f_side = col_u2.file_uploader("측면 영상 (Side View)", type=['mp4', 'mov'])

if f_front or f_side:
    v_col1, v_col2 = st.columns(2)
    if f_front:
        with v_col1:
            st.subheader("📸 Front View Analysis")
            v_b64_f = base64.b64encode(f_front.read()).decode()
            components.html(get_advanced_engine(v_b64_f, "FRONT"), height=700)
    if f_side:
        with v_col2:
            st.subheader("📸 Side View Analysis")
            v_b64_s = base64.b64encode(f_side.read()).decode()
            components.html(get_advanced_engine(v_b64_s, "SIDE"), height=700)

    st.divider()

    # [4] 데이터 통합 기술 리포트
    st.header("🔬 고차원 역학 통합 진단")
    c1, c2, c3, c4 = st.columns(4)
    in_x = c1.number_input("Max X-Factor (Deg)", min_value=0.0, step=0.1)
    in_sp = c2.number_input("Max Wrist Speed (m/s)", min_value=0.0, step=0.1)
    in_s_s = c3.number_input("Side Δ Spine (Deg)", min_value=0.0, step=0.1)
    in_sw = c4.number_input("Front Sway (px)", min_value=0.0, step=1.0)

    if st.button("🚀 정밀 역학 리포트 생성") and model:
        with st.spinner("Gemini 엔진이 복합 역학 데이터를 분석 중입니다..."):
            prompt = f"""
            운동역학 전문가로서 다음 통합 데이터를 기반으로 기술 진단을 수행하십시오.
            - X-Factor(상하체 분리 각도): {in_x}°
            - 손목 최대 속도(헤드 스피드 지표): {in_sp}m/s
            - 척추각 편차(측면): {in_s_s}°
            - 골반 스웨이(정면): {in_sw}px
            
            1. X-Factor와 손목 속도의 상관관계를 통해 에너지 생성 효율을 분석하십시오.
            2. 척추각 유지와 골반 스웨이가 정타율(Smash Factor)에 미치는 영향을 기술하십시오.
            3. 보상 동작을 억제하기 위한 물리적 교정안을 제시하십시오.
            철저히 기술적/물리적 관점에서만 서술하십시오.
            """
            response = model.generate_content(prompt)
            st.markdown("### 🤖 데이터 기반 기술 진단")
            st.write(response.text)
