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

st.set_page_config(layout="wide", page_title="GDR AI Engine v42")
st.title("⛳ GDR AI Pro: 정면/측면 역학 지표 정밀 구분 v42.0")

# [2] 분석 엔진 (라벨링 및 데이터 구분 강화)
def get_labeled_engine(v_b64, label):
    # 정면과 측면에 따라 표시할 텍스트를 다르게 설정
    stats_html = ""
    if label == "FRONT":
        stats_html = """
            <b>[FRONT VIEW]</b><br>
            Sway: <span id="sw_v">0.0</span>px<br>
            X-Factor: <span id="x_v">0.0</span>°<br>
            Tilt: <span id="t_v">0.0</span>°
        """
    else:
        stats_html = """
            <b>[SIDE VIEW]</b><br>
            Δ Spine: <span id="s_v">0.0</span>°<br>
            Knee: <span id="k_v">0.0</span>°<br>
            Wrist Spd: <span id="sp_v">0.0</span>m/s
        """

    return f"""
    <div style="width:100%; background:#000; border-radius:12px; overflow:hidden; position:relative; border: 2px solid #333;">
        <video id="v" controls playsinline style="width:100%; display:block; aspect-ratio:9/16;"></video>
        <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
        <div id="stats" style="position:absolute; top:10px; right:10px; background:rgba(0,0,0,0.85); color:#0f0; padding:15px; border-radius:8px; font-family:monospace; border:1px solid #0f0; font-size:13px; z-index:1000; line-height:1.6;">
            {stats_html}
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const v=document.getElementById('v'), c=document.getElementById('c'), ctx=c.getContext('2d');
        const sD=document.getElementById('s_v'), swD=document.getElementById('sw_v'), 
              xD=document.getElementById('x_v'), tD=document.getElementById('t_v'), 
              spD=document.getElementById('sp_v'), kD=document.getElementById('k_v');
        
        let minS=180, maxS=0, startX=0, lastWristPos=null, lastTime=0, maxWristSpeed=0, angleHistory=[];

        const pose=new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:1, smoothLandmarks:true}});
        
        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            c.width=v.videoWidth; c.height=v.videoHeight;
            ctx.clearRect(0,0,c.width,c.height);
            const lm = r.poseLandmarks;
            const now = performance.now();

            const sh_c = {{x:(lm[11].x+lm[12].x)/2, y:(lm[11].y+lm[12].y)/2}};
            const h_c = {{x:(lm[23].x+lm[24].x)/2, y:(lm[23].y+lm[24].y)/2}};

            if("{label}" === "FRONT") {{
                // Sway 계산
                if(startX===0) startX = h_c.x;
                swD.innerText = (Math.abs(h_c.x - startX) * c.width).toFixed(1);
                // X-Factor 계산
                const shRot = Math.atan2(lm[12].y-lm[11].y, lm[12].x-lm[11].x)*180/Math.PI;
                const hRot = Math.atan2(lm[24].y-lm[23].y, lm[24].x-lm[23].x)*180/Math.PI;
                xD.innerText = Math.abs(shRot - hRot).toFixed(1);
                // 어깨 Tilt
                tD.innerText = Math.abs(shRot).toFixed(1);
            }} else {{
                // Δ Spine 계산
                const curA = Math.abs(Math.atan2(h_c.y-sh_c.y, h_c.x-sh_c.x)*180/Math.PI);
                angleHistory.push(curA); if(angleHistory.length>3) angleHistory.shift();
                const fA = angleHistory.reduce((a,b)=>a+b)/angleHistory.length;
                if(fA<minS) minS=fA; if(fA>maxS) maxS=fA;
                sD.innerText = (maxS-minS).toFixed(1);
                // 무릎 각도
                kD.innerText = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI).toFixed(1);
                // Wrist Speed
                const wrist = lm[15];
                if(lastWristPos && lastTime > 0) {{
                    const dt = (now - lastTime) / 1000;
                    const dist = Math.sqrt(Math.pow(wrist.x-lastWristPos.x, 2) + Math.pow(wrist.y-lastWristPos.y, 2));
                    const speed = (dist * 2.0) / dt;
                    if(speed > maxWristSpeed) maxWristSpeed = speed;
                    spD.innerText = maxWristSpeed.toFixed(1);
                }}
                lastWristPos = {{x:wrist.x, y:wrist.y}}; lastTime = now;
            }}

            ctx.strokeStyle = '#00FF00'; ctx.lineWidth = 4;
            ctx.beginPath(); ctx.moveTo(sh_c.x*c.width, sh_c.y*c.height); ctx.lineTo(h_c.x*c.width, h_c.y*c.height); ctx.stroke();
        }});
        
        const blob = new Blob([Uint8Array.from(atob("{v_b64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}});
        v.src = URL.createObjectURL(blob);
        v.onplay = async () => {{ while(!v.paused && !v.ended){{ await pose.send({{image:v}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
    </script>
    """

# [3] 파일 업로드 섹션
col_u1, col_u2 = st.columns(2)
f_front = col_u1.file_uploader("정면 영상 업로드 (Sway / X-Factor)", type=['mp4', 'mov'])
f_side = col_u2.file_uploader("측면 영상 업로드 (Δ Spine / Knee)", type=['mp4', 'mov'])

if f_front or f_side:
    v_col1, v_col2 = st.columns(2)
    if f_front:
        with v_col1:
            st.subheader("📸 Front Analysis (정면)")
            v_b64_f = base64.b64encode(f_front.read()).decode()
            components.html(get_labeled_engine(v_b64_f, "FRONT"), height=700)
    if f_side:
        with v_col2:
            st.subheader("📸 Side Analysis (측면)")
            v_b64_s = base64.b64encode(f_side.read()).decode()
            components.html(get_labeled_engine(v_b64_s, "SIDE"), height=700)

    st.divider()

    # [4] 데이터 통합 입력 및 리포트 (기술적 분석 전용)
    st.header("🔬 전문 역학 통합 진단 데이터 입력")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("**[FRONT DATA]**")
        in_sway = st.number_input("Sway (px)", min_value=0.0, step=1.0)
        in_xfactor = st.number_input("X-Factor (Deg)", min_value=0.0, step=0.1)
    with c2:
        st.markdown("**[SIDE DATA]**")
        in_spine = st.number_input("Δ Spine (Deg)", min_value=0.0, step=0.1)
        in_knee = st.number_input("Knee Angle (Deg)", min_value=0.0, step=0.1)
    with c3:
        st.markdown("**[PERFORMANCE]**")
        in_speed = st.number_input("Wrist Speed (m/s)", min_value=0.0, step=0.1)

    if st.button("🚀 종합 기술 분석 리포트 생성") and model:
        with st.spinner("다각도 물리 데이터를 통합 해석 중입니다..."):
            prompt = f"""
            골프 운동역학 전문가로서 다음 정면/측면 데이터를 기술적으로 분석하십시오.
            [정면] Sway: {in_sway}px, X-Factor: {in_xfactor}°
            [측면] Δ Spine: {in_spine}°, Knee: {in_knee}°
            [성능] Wrist Speed: {in_speed}m/s
            
            1. 하체 지지력(Sway)과 상체 꼬임(X-Factor)의 효율성을 분석하십시오.
            2. 척추각 유지와 무릎 각도가 임팩트 일관성에 미치는 물리적 영향을 설명하십시오.
            3. 데이터 기반의 기술적 교정 방향을 제시하십시오.
            전문적이고 냉철한 어조로 작성하며 개인적인 언급은 배제하십시오.
            """
            response = model.generate_content(prompt)
            st.markdown("### 🤖 데이터 통합 진단 리포트")
            st.write(response.text)
