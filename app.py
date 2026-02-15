import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import base64

# [1] Gemini 보안 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-pro') 
except Exception:
    st.error("Gemini API 키 설정을 확인해주세요.")
    st.stop()

st.set_page_config(layout="wide", page_title="GDR AI Pro v29")
st.title("⛳ GDR AI Pro: 수치 분석 통합 버전 v29.0")

# [2] 실시간 수치 추출 엔진 (팝업형 레이아웃)
def get_data_engine(v_src):
    return f"""
    <div style="width:100%; background:#000; border-radius:10px; overflow:hidden; position:relative; border: 2px solid #0f0;">
        <video id="v" controls playsinline style="width:100%; display:block; aspect-ratio:9/16;"></video>
        <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
        <div style="position:absolute; top:10px; right:10px; background:rgba(0,0,0,0.8); color:#0f0; padding:10px; border-radius:5px; font-family:monospace; z-index:1000; border:1px solid #0f0; font-size:18px;">
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
        v.onplay = async () => {{ while(!v.paused && !v.ended){{ await pose.send({{image:v}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
    </script>
    """

# [3] 메인 레이아웃 (좌측 영상 / 우측 리포트)
f = st.file_uploader("영상을 업로드하세요", type=['mp4', 'mov'])

if f:
    col_left, col_right = st.columns([1.2, 1])
    
    with col_left:
        st.subheader("🎥 실시간 수치 분석기")
        v_base64 = base64.b64encode(f.read()).decode()
        v_src = f"data:video/mp4;base64,{v_base64}"
        components.html(get_data_engine(v_src), height=750)
        st.caption("※ 영상 우측 상단의 Δ Spine 수치를 확인하세요.")

    with col_right:
        st.header("📋 Gemini Pro 심층 리포트")
        st.info("6월에 태어날 아기를 위해 최고의 스윙을 만들어봅시다! 👶")
        
        # 분석기에서 확인한 수치를 여기에 입력
        s_val = st.number_input("분석기에서 확인한 Δ Spine 수치 입력", min_value=0.0, step=0.1)
        
        if s_val > 0:
            if st.button("🔄 Gemini AI 분석 결과 보기"):
                with st.spinner("전문 역학 데이터 해석 중..."):
                    prompt = f"척추각 편차 {s_val}도인 골퍼에게 운동학적 사슬 분석을 해주고 6월 아빠를 격려해줘. 한국어로 답변해."
                    response = model.generate_content(prompt)
                    st.chat_message("assistant").write(response.text)
                    
                    st.divider()
                    st.subheader("📸 프로 스윙 가이드")
                    st.image("https://img.vavel.com/tiger-woods-swing-1608144214553.jpg", caption="이상적인 척추각 유지")
                    st.video("https://www.youtube.com/watch?v=VrOGGXdf_tM" if s_val > 4 else "https://www.youtube.com/watch?v=2vT64W2XfC0")

st.sidebar.markdown(f"**Baby Due: June 2026** 👶")
