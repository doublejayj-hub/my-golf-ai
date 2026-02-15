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

st.set_page_config(layout="wide", page_title="GDR AI Engine v38")
st.title("⛳ GDR AI Pro: 고정밀 역학 데이터 추출 엔진 v38.0")

# [2] 전문 역학 연산 자바스크립트 엔진
def get_expert_engine(v_b64, label):
    return f"""
    <div style="width:100%; background:#000; border-radius:12px; overflow:hidden; position:relative; border: 2px solid #333;">
        <video id="v" controls playsinline style="width:100%; display:block; aspect-ratio:9/16;"></video>
        <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
        <div id="stats" style="position:absolute; top:10px; right:10px; background:rgba(0,0,0,0.85); color:#0f0; padding:15px; border-radius:8px; font-family:monospace; border:1px solid #0f0; font-size:13px; z-index:1000; line-height:1.6;">
            <b style="color:#fff; border-bottom:1px solid #555;">[MECHANICAL DATA]</b><br>
            Δ Spine: <span id="s_v">0.0</span>°<br>
            Sway: <span id="sw_v">0.0</span>px<br>
            Tilt: <span id="r_v">0.0</span>°<br>
            Knee: <span id="k_v">0.0</span>°
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const v=document.getElementById('v'), c=document.getElementById('c'), ctx=c.getContext('2d');
        const sD=document.getElementById('s_v'), swD=document.getElementById('sw_v'), rD=document.getElementById('r_v'), kD=document.getElementById('k_v');
        
        let minS=180, maxS=0, startX=0;

        const pose=new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:1, smoothLandmarks:true}});
        
        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            c.width=v.videoWidth; c.height=v.videoHeight;
            ctx.clearRect(0,0,c.width,c.height);
            const lm = r.poseLandmarks;

            // 1. 척추각(Spine Angle) 연산
            const sh_c = {{x:(lm[11].x+lm[12].x)/2, y:(lm[11].y+lm[12].y)/2}};
            const h_c = {{x:(lm[23].x+lm[24].x)/2, y:(lm[23].y+lm[24].y)/2}};
            const spine = Math.abs(Math.atan2(h_c.y-sh_c.y, h_c.x-sh_c.x)*180/Math.PI);
            if(spine<minS) minS=spine; if(spine>maxS) maxS=spine;
            sD.innerText = (maxS-minS).toFixed(1);

            // 2. 골반 좌우 변위(Sway) 연산
            if(startX===0) startX = h_c.x;
            swD.innerText = (Math.abs(h_c.x - startX) * c.width).toFixed(1);

            // 3. 어깨 기울기(Shoulder Tilt) 연산
            const tilt = Math.abs(Math.atan2(lm[12].y-lm[11].y, lm[12].x-lm[11].x)*180/Math.PI);
            rD.innerText = tilt.toFixed(1);

            // 4. 무릎 유지력(Knee Angle) 연산
            const knee = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI);
            kD.innerText = knee.toFixed(1);

            // 시각화 가이드라인 (Spine Line)
            ctx.strokeStyle = '#00FF00'; ctx.lineWidth = 4;
            ctx.beginPath(); ctx.moveTo(sh_c.x*c.width, sh_c.y*c.height); ctx.lineTo(h_c.x*c.width, h_c.y*c.height); ctx.stroke();
        }});
        
        const blob = new Blob([Uint8Array.from(atob("{v_b64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}});
        v.src = URL.createObjectURL(blob);
        v.onplay = async () => {{ while(!v.paused && !v.ended){{ await pose.send({{image:v}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
    </script>
    """

# [3] 레이아웃 구성
f_f = st.file_uploader("분석할 스윙 영상을 업로드하세요", type=['mp4', 'mov'])

if f_f:
    col_left, col_right = st.columns([1.5, 1])
    with col_left:
        st.subheader("🎥 실시간 물리 데이터 추출")
        v_b64 = base64.b64encode(f_f.read()).decode()
        components.html(get_expert_engine(v_b64, "ANALYSIS"), height=750)

    with col_right:
        st.header("📋 데이터 심층 분석 리포트")
        st.markdown("추출된 물리 지표를 입력하여 Gemini의 기술적 진단을 받으세요.")
        
        c1, c2 = st.columns(2)
        s_val = c1.number_input("Δ Spine (Deg)", min_value=0.0, step=0.1)
        sw_val = c2.number_input("Sway (Pixel)", min_value=0.0, step=1.0)
        
        if (s_val > 0 or sw_val > 0) and model:
            if st.button("🚀 정밀 역학 진단 시작"):
                with st.spinner("Gemini 엔진이 물리 데이터를 해석 중입니다..."):
                    prompt = f"""
                    골프 운동역학 전문가로서 아래 데이터를 기술적으로 분석하십시오.
                    - 척추각 편차: {s_val}도
                    - 골반 스웨이: {sw_val}px
                    
                    1. 척추축 안정성과 하체 지지력의 상관관계를 물리적으로 설명하십시오.
                    2. 효율적인 에너지 전달(Kinematic Sequence)을 위한 기술적 교정안을 제시하십시오.
                    불필요한 미사여구 없이 데이터 기반의 분석만 제공하십시오.
                    """
                    response = model.generate_content(prompt)
                    st.chat_message("assistant").write(response.text)
                    
                    st.divider()
                    st.subheader("📺 추천 교정 훈련")
                    yt = "https://www.youtube.com/watch?v=VrOGGXdf_tM" if s_val > 5 else "https://www.youtube.com/watch?v=2vT64W2XfC0"
                    st.video(yt)
