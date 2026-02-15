import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import base64

# [1] 시스템 자가 진단: 사용 가능한 모델 리스트 강제 조회
def initialize_gemini():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # 현재 서버 환경에서 지원하는 모델 목록을 직접 가져옵니다.
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 1순위: 1.5-flash, 2순위: gemini-pro, 3순위: 목록의 첫 번째 모델
        selected_model_name = ""
        if 'models/gemini-1.5-flash' in available_models:
            selected_model_name = 'models/gemini-1.5-flash'
        elif 'models/gemini-pro' in available_models:
            selected_model_name = 'models/gemini-pro'
        elif available_models:
            selected_model_name = available_models[0]
        
        if selected_model_name:
            st.sidebar.success(f"연결된 모델: {selected_model_name}")
            return genai.GenerativeModel(selected_model_name)
        else:
            st.error("사용 가능한 Gemini 모델을 찾을 수 없습니다.")
            return None
    except Exception as e:
        st.error(f"모델 초기화 중 치명적 오류: {e}")
        return None

model = initialize_gemini()

st.set_page_config(layout="wide", page_title="GDR AI v35.0")
st.title("⛳ GDR AI Pro: 모델 자가 진단 버전 v35.0")

# [2] 하이브리드 수치 안정화 엔진 (이동 평균 필터 유지)
def get_pro_engine(v_b64):
    return f"""
    <div id="container" style="width:100%; background:#000; border-radius:15px; overflow:hidden; position:relative;">
        <video id="v" controls playsinline style="width:100%; display:block; aspect-ratio:9/16; background:#000;"></video>
        <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
        <div style="position:absolute; top:20px; right:20px; background:rgba(0,0,0,0.85); color:#0f0; padding:12px 18px; border-radius:10px; font-family:monospace; border:1px solid #0f0; z-index:1000; font-size:18px;">
            Δ Spine: <span id="val">0.0</span>°
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const v=document.getElementById('v'), c=document.getElementById('c'), ctx=c.getContext('2d'), res=document.getElementById('val');
        let maxS=0, minS=180;
        let angleHistory = []; 

        const pose=new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:1, smoothLandmarks:true}});
        
        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            c.width=v.videoWidth; c.height=v.videoHeight;
            ctx.clearRect(0,0,c.width,c.height);
            const sh=r.poseLandmarks[11], h=r.poseLandmarks[23];
            const currentAngle = Math.abs(Math.atan2(h.y-sh.y, h.x-sh.x)*180/Math.PI);

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

# [3] 메인 화면 구성
f = st.file_uploader("분석할 영상을 업로드하세요", type=['mp4', 'mov'])

if f:
    col_v, col_r = st.columns([1.3, 1])
    with col_v:
        st.subheader("🎥 실시간 역학 분석기")
        v_b64 = base64.b64encode(f.read()).decode()
        components.html(get_pro_engine(v_b64), height=750)

    with col_r:
        st.header("📋 AI 지능형 리포트")
        st.success("6월에 태어날 아기에게 보여줄 멋진 아빠의 스윙! 👶")
        
        s_val = st.number_input("위 분석기에서 확인된 Δ Spine 수치를 입력하세요", min_value=0.0, step=0.1)
        
        if s_val > 0 and model:
            if st.button("🔄 Gemini AI 전문 분석 시작"):
                with st.spinner("최적화된 Gemini 엔진이 리포트를 작성 중입니다..."):
                    try:
                        prompt = f"척추각 편차 {s_val}도인 골퍼에게 전문적인 역학 분석을 해주고 6월 아빠를 격려해줘. 한국어로 답변해."
                        response = model.generate_content(prompt)
                        st.chat_message("assistant").write(response.text)
                        
                        st.divider()
                        st.subheader("📺 추천 교정 레슨")
                        yt_link = "https://www.youtube.com/watch?v=VrOGGXdf_tM" if s_val > 4 else "https://www.youtube.com/watch?v=2vT64W2XfC0"
                        st.video(yt_link)
                    except Exception as e:
                        st.error(f"리포트 생성 중 오류: {e}")

st.sidebar.markdown(f"**Baby Due: June 2026** 👶")
