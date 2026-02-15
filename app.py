import streamlit as st
import streamlit.components.v1 as components
import base64
import google.generativeai as genai

# [1] Gemini 보안 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception:
    st.error("Secrets 설정 오류: GEMINI_API_KEY를 확인하세요.")
    st.stop()

st.set_page_config(layout="centered", page_title="GDR AI Final")
st.title("⛳ GDR AI Pro: 고성능 스윙 분석기 v18.0")

# [2] 하이퍼 안정화 엔진
def get_final_engine(v_src):
    return f"""
    <div id="container" style="width:100%; background:#000; border-radius:15px; overflow:hidden; position:relative; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
        <video id="v" controls playsinline style="width:100%; display:block; aspect-ratio:9/16;"></video>
        <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
        <div id="hud" style="position:absolute; top:20px; right:20px; background:rgba(0,0,0,0.8); color:#0f0; padding:10px 15px; border-radius:8px; font-family:monospace; border:1px solid #0f0; z-index:1000; font-size:16px;">
            Δ Spine: <span id="val">0.0</span>°
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const v=document.getElementById('v'), c=document.getElementById('c'), ctx=c.getContext('2d'), res=document.getElementById('val');
        let maxS=0, minS=180;

        const pose=new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` or `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:1, smoothLandmarks:true, minDetectionConfidence:0.5, minTrackingConfidence:0.5}});
        
        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            c.width=v.videoWidth; c.height=v.videoHeight;
            ctx.save(); ctx.clearRect(0,0,c.width,c.height);
            const sh=r.poseLandmarks[11], h=r.poseLandmarks[23];
            const spine = Math.abs(Math.atan2(h.y-sh.y, h.x-sh.x)*180/180*Math.PI);
            if(spine > 0) {{
                if(spine > maxS) maxS = spine; if(spine < minS) minS = spine;
                res.innerText = (maxS - minS).toFixed(1);
            }}
            ctx.restore();
        }});

        // [중요] 브라우저 직접 로드 방식
        v.src = "{v_src}";
        v.addEventListener('loadeddata', () => {{
            v.onplay = async function(){{ while(!v.paused && !v.ended){{ await pose.send({{image:v}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
        }});
    </script>
    """

# [3] 메인 레이아웃
f = st.file_uploader("영상을 업로드하세요 (정면/측면 무관)", type=['mp4', 'mov'])

if f:
    v_src = "data:video/mp4;base64," + base64.b64encode(f.read()).decode()
    components.html(get_final_engine(v_src), height=700)
    
    st.divider()
    
    # [4] 데이터 기반 지능형 리포트 (실시간 입력 브릿지)
    st.header("📋 Gemini Pro 심층 역학 진단")
    s_val = st.number_input("영상 우측 상단의 Δ Spine 수치를 입력하세요", min_value=0.0, step=0.1)
    
    if s_val > 0:
        if st.button("🔄 Gemini 실시간 분석 가동"):
            with st.spinner("전문 역학 분석 중..."):
                prompt = f"척추각 편차 {s_val}도인 골퍼를 위해 운동학적 사슬 분석을 해주고 6월 아빠를 격려해줘."
                response = model.generate_content(prompt)
                st.chat_message("assistant").write(response.text)
                st.video("https://www.youtube.com/watch?v=VrOGGXdf_tM" if s_val > 4 else "https://www.youtube.com/watch?v=2vT64W2XfC0")

st.sidebar.markdown(f"**Baby Due: June 2026** 👶")
