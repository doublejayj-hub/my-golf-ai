import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import base64

# [1] Gemini 보안 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-pro') 
except Exception:
    st.error("Gemini API 인증 실패. Secrets를 확인하세요.")
    st.stop()

st.set_page_config(layout="centered", page_title="GDR AI Final")
st.title("⛳ GDR AI Pro: 최종 재생 보장 버전 v24.0")

# [2] 하이퍼 안정화 엔진 (영상 우선 로드 방식)
def get_guaranteed_engine(v_base64):
    return f"""
    <div style="width:100%; background:#000; border-radius:15px; overflow:hidden; position:relative;">
        <video id="v" controls playsinline style="width:100%; display:block; aspect-ratio:9/16; background:#000;"></video>
        <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
        <div style="position:absolute; top:15px; right:15px; background:rgba(0,0,0,0.8); color:#0f0; padding:8px 12px; border-radius:5px; font-family:monospace; border:1px solid #0f0; z-index:1000; font-size:15px;">
            Δ Spine: <span id="val">0.0</span>°
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose/pose.js"></script>
    <script>
        const v=document.getElementById('v'), c=document.getElementById('c'), ctx=c.getContext('2d'), res=document.getElementById('val');
        let maxS=0, minS=180;

        // 1. 영상 소스 주입 (가장 표준적인 데이터 URL 방식)
        v.src = "data:video/mp4;base64,{v_base64}";

        // 2. MediaPipe Pose 초기화 (영상과 독립적으로 실행)
        const pose = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` or `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:1, smoothLandmarks:true}});
        pose.onResults((r) => {{
            if(!r.poseLandmarks) return;
            c.width=v.videoWidth; c.height=v.videoHeight;
            ctx.clearRect(0,0,c.width,c.height);
            const sh=r.poseLandmarks[11], h=r.poseLandmarks[23];
            const spine = Math.abs(Math.atan2(h.y-sh.y, h.x-sh.x)*180/Math.PI);
            if(spine > 0) {{
                if(spine > maxS) maxS = spine; if(spine < minS) minS = spine;
                res.innerText = (maxS - minS).toFixed(1);
            }}
            ctx.strokeStyle = '#00FF00'; ctx.lineWidth = 5;
            ctx.beginPath(); ctx.moveTo(sh.x*c.width, sh.y*c.height); ctx.lineTo(h.x*c.width, h.y*c.height); ctx.stroke();
        }});

        v.onplay = async () => {{ 
            while(!v.paused && !v.ended) {{ 
                try {{ await pose.send({{image:v}}); }} catch(e) {{ console.error(e); }}
                await new Promise(r=>requestAnimationFrame(r)); 
            }} 
        }};
    </script>
    """

# [3] UI 구성
f = st.file_uploader("스윙 영상 업로드", type=['mp4', 'mov'])

if f:
    v_base64 = base64.b64encode(f.read()).decode()
    # height를 영상 비율에 맞춰 700으로 고정하여 잘림 방지
    components.html(get_guaranteed_engine(v_base64), height=700)
    
    st.divider()
    
    # [4] AI 심층 역학 리포트 (사용자 입력 브릿지)
    st.header("📋 AI 지능형 역학 리포트")
    s_val = st.number_input("영상 우측 상단의 Δ Spine 수치를 입력하세요", min_value=0.0, step=0.1)
    
    if s_val > 0:
        if st.button("🔄 Gemini AI 분석 가동"):
            with st.spinner("전문 역학 분석 중..."):
                prompt = f"척추각 편차 {s_val}도인 골퍼를 위해 운동학적 사슬 분석을 해주고 6월 아빠를 격려해줘. 한국어로 답변해줘."
                response = model.generate_content(prompt)
                st.chat_message("assistant").write(response.text)
                st.video("https://www.youtube.com/watch?v=VrOGGXdf_tM" if s_val > 4 else "https://www.youtube.com/watch?v=2vT64W2XfC0")

st.sidebar.markdown(f"**Baby Due: June 2026** 👶")
