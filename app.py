import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import base64

# [1] Gemini 자가 진단 및 모델 강제 할당 (v35 로직 유지)
def initialize_gemini():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 최신 모델 우선 순위 할당
        for model_name in ['models/gemini-1.5-flash', 'models/gemini-pro']:
            if model_name in available_models:
                return genai.GenerativeModel(model_name)
        return genai.GenerativeModel(available_models[0]) if available_models else None
    except Exception as e:
        st.error(f"모델 초기화 오류: {e}")
        return None

model = initialize_gemini()

st.set_page_config(layout="wide", page_title="GDR AI Pro v36")
st.title("⛳ GDR AI Pro: 다각도 지능형 역학 분석 v36.0")

# [2] 고정밀 역학 분석 엔진 (3프레임 필터 탑재)
def get_analysis_engine(v_b64, label):
    return f"""
    <div style="width:100%; background:#000; border-radius:12px; overflow:hidden; position:relative; border: 2px solid #444;">
        <video id="v_{label}" controls playsinline style="width:100%; display:block; aspect-ratio:9/16; background:#000;"></video>
        <canvas id="c_{label}" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
        <div style="position:absolute; top:15px; right:15px; background:rgba(0,0,0,0.8); color:#0f0; padding:10px 15px; border-radius:8px; font-family:monospace; border:1px solid #0f0; z-index:1000; font-size:16px;">
            {label} Δ Spine: <span id="val_{label}">0.0</span>°
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const v=document.getElementById('v_{label}'), c=document.getElementById('c_{label}'), ctx=c.getContext('2d'), res=document.getElementById('val_{label}');
        let maxS=0, minS=180, angleHistory=[];

        const pose=new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:1, smoothLandmarks:true}});
        
        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            c.width=v.videoWidth; c.height=v.videoHeight;
            ctx.clearRect(0,0,c.width,c.height);
            const sh=r.poseLandmarks[11], h=r.poseLandmarks[23];
            const currentAngle = Math.abs(Math.atan2(h.y-sh.y, h.x-sh.x)*180/Math.PI);

            // 3프레임 이동 평균 필터 적용 (수치 안정화)
            angleHistory.push(currentAngle);
            if(angleHistory.length > 3) angleHistory.shift();
            const filteredAngle = angleHistory.reduce((a,b)=>a+b)/angleHistory.length;

            if(filteredAngle > 0) {{
                if(filteredAngle > maxS) maxS = filteredAngle; 
                if(filteredAngle < minS) minS = filteredAngle;
                res.innerText = (maxS - minS).toFixed(1);
            }}
            ctx.strokeStyle = '#00FF00'; ctx.lineWidth = 5;
            ctx.beginPath(); ctx.moveTo(sh.x*c.width, sh.y*c.height); ctx.lineTo(h.x*c.width, h.y*c.height); ctx.stroke();
        }});
        
        const blob = new Blob([Uint8Array.from(atob("{v_b64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}});
        v.src = URL.createObjectURL(blob);
        v.onplay = async () => {{ while(!v.paused && !v.ended){{ await pose.send({{image:v}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
    </script>
    """

# [3] UI 레이아웃 구성
st.sidebar.header("📊 분석 설정")
st.sidebar.success(f"연결 모델: {model.model_name if model else 'None'}")

f_front = st.file_uploader("정면 영상 업로드 (Front)", type=['mp4', 'mov'], key="f")
f_side = st.file_uploader("측면 영상 업로드 (Side)", type=['mp4', 'mov'], key="s")

if f_front or f_side:
    col1, col2 = st.columns(2)
    
    with col1:
        if f_front:
            st.subheader("📸 정면 분석")
            v_b64_f = base64.b64encode(f_front.read()).decode()
            components.html(get_analysis_engine(v_b64_f, "FRONT"), height=700)
    
    with col2:
        if f_side:
            st.subheader("📸 측면 분석")
            v_b64_s = base64.b64encode(f_side.read()).decode()
            components.html(get_analysis_engine(v_b64_s, "SIDE"), height=700)

    st.divider()

    # [4] 데이터 기반 지능형 리포트
    st.header("📝 Gemini AI 통합 역학 진단")
    
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        s_front = st.number_input("정면 Δ Spine 입력", min_value=0.0, step=0.1)
    with c2:
        s_side = st.number_input("측면 Δ Spine 입력", min_value=0.0, step=0.1)
    
    with c3:
        if (s_front > 0 or s_side > 0) and model:
            if st.button("🚀 Gemini 전문 리포트 생성"):
                with st.spinner("다각도 데이터를 통합 분석 중입니다..."):
                    try:
                        prompt = f"""
                        당신은 세계적인 골프 물리 역학 전문가입니다.
                        정면 척추각 편차: {s_front}도, 측면 척추각 편차: {s_side}도.
                        
                        1. 각 뷰(View)의 수치를 바탕으로 지면 반력, 회전축 유지, 얼리 익스텐션 여부를 분석하세요.
                        2. 척추각 고정을 위한 핵심 훈련법(Drill)을 원론적으로 제시하세요.
                        한국어로 정중하고 전문적으로 답변해주세요.
                        """
                        response = model.generate_content(prompt)
                        st.markdown("### 🤖 분석 결과")
                        st.write(response.text)
                        
                        st.divider()
                        st.subheader("📺 추천 교정 가이드")
                        yt = "https://www.youtube.com/watch?v=VrOGGXdf_tM" if (s_front + s_side)/2 > 4 else "https://www.youtube.com/watch?v=2vT64W2XfC0"
                        st.video(yt)
                    except Exception as e:
                        st.error(f"리포트 생성 중 오류: {e}")
        else:
            st.warning("분석기에서 확인된 Δ Spine 수치를 입력하면 리포트가 생성됩니다.")

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Baby Due: June 2026** 👶")
