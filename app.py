import streamlit as st
import google.generativeai as genai
import base64

# [1] Gemini 보안 설정 (호환성 높은 모델명 사용)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # 404 에러 방지를 위해 가장 안정적인 모델명으로 설정합니다.
    model = genai.GenerativeModel('gemini-pro') 
except Exception as e:
    st.error(f"Gemini API 키 설정을 확인해주세요: {e}")
    st.stop()

st.set_page_config(layout="centered", page_title="GDR AI Pro v20")
st.title("⛳ GDR AI Pro: 지능형 역학 분석 v20.0")

# [2] 하이퍼 안정화 엔진 (재생 보장형)
def get_final_engine(v_src):
    return f"""
    <div id="container" style="width:100%; background:#000; border-radius:15px; overflow:hidden; position:relative;">
        <video id="v" controls playsinline style="width:100%; display:block; aspect-ratio:9/16;"></video>
        <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
        <div style="position:absolute; top:20px; right:20px; background:rgba(0,0,0,0.8); color:#0f0; padding:10px 15px; border-radius:8px; font-family:monospace; border:1px solid #0f0; z-index:1000; font-size:16px;">
            Δ Spine: <span id="val">0.0</span>°
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const v=document.getElementById('v'), c=document.getElementById('c'), ctx=c.getContext('2d'), res=document.getElementById('val');
        let maxS=0, minS=180;
        const pose=new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` or `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:1, smoothLandmarks:true}});
        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            c.width=v.videoWidth; c.height=v.videoHeight;
            ctx.clearRect(0,0,c.width,c.height);
            const sh=r.poseLandmarks[11], h=r.poseLandmarks[23];
            const spine = Math.abs(Math.atan2(h.y-sh.y, h.x-sh.x)*180/Math.PI);
            if(spine > 0) {{
                if(spine > maxS) maxS = spine; if(spine < minS) minS = spine;
                res.innerText = (maxS - minS).toFixed(1);
            }}
            ctx.strokeStyle = '#00FF00'; ctx.lineWidth = 4;
            ctx.beginPath(); ctx.moveTo(sh.x*c.width, sh.y*c.height); ctx.lineTo(h.x*c.width, h.y*c.height); ctx.stroke();
        }});
        v.src = "{v_src}";
        v.onloadedmetadata = () => {{ v.onplay = async () => {{ while(!v.paused && !v.ended){{ await pose.send({{image:v}}); await new Promise(r=>requestAnimationFrame(r)); }} }}; }};
    </script>
    """

# [3] 메인 레이아웃
f = st.file_uploader("스윙 영상 업로드 (MP4/MOV)", type=['mp4', 'mov'])

if f:
    v_src = "data:video/mp4;base64," + base64.b64encode(f.read()).decode()
    components.html(get_final_engine(v_src), height=700)
    
    st.divider()
    
    # [4] AI 심층 역학 리포트
    st.header("📋 AI 지능형 역학 리포트")
    s_val = st.number_input("영상 우측 상단의 Δ Spine 수치를 입력하세요", min_value=0.0, step=0.1)
    
    if s_val > 0:
        if st.button("🔄 Gemini AI 분석 가동"):
            with st.spinner("Gemini Pro가 운동학적 사슬을 분석 중입니다..."):
                try:
                    # 원론적 분석을 강화한 프롬프트
                    prompt = f"""
                    당신은 세계 최고의 골프 역학 전문가입니다. 다음 분석 데이터를 바탕으로 리포트를 작성해주세요.
                    - 측정된 척추각 편차(Δ Spine): {s_val}도
                    
                    1. 이 수치가 암시하는 운동학적 사슬(Kinematic Sequence)의 문제를 설명할 것. (특히 배치기/Early Extension 관련)
                    2. 지면 반력과 회전 축 유지 관점에서 개선해야 할 원론적인 교정 방향을 제시할 것.
                    3. 6월에 아빠가 될 골퍼에게 따뜻한 격려를 한마디 덧붙일 것.
                    4. 전문적인 어조를 사용하되 이해하기 쉽게 설명할 것.
                    """
                    response = model.generate_content(prompt)
                    st.chat_message("assistant").write(response.text)
                    
                    st.divider()
                    st.subheader("📸 프로 스윙 레퍼런스")
                    st.image("https://img.vavel.com/tiger-woods-swing-1608144214553.jpg", 
                             caption="Tiger Woods: 척추각과 하체 리드의 정석")
                    
                    st.subheader("📺 추천 교정 레슨")
                    yt_link = "https://www.youtube.com/watch?v=VrOGGXdf_tM" if s_val > 4 else "https://www.youtube.com/watch?v=2vT64W2XfC0"
                    st.video(yt_link)
                except Exception as e:
                    st.error(f"Gemini 모델 호출 중 오류가 발생했습니다: {e}")
