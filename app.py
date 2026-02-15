import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import tempfile
import os

# [1] Gemini 보안 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-pro') 
except Exception:
    st.error("Gemini API 키 설정을 확인해주세요.")
    st.stop()

st.set_page_config(layout="wide", page_title="GDR AI Pro v30")
st.title("⛳ GDR AI Pro: 최종 수율 안정화 버전 v30.0")

# [2] 하이퍼 라이트 분석 엔진 (분석부 분리형)
def get_light_engine(video_file):
    # 영상을 임시 URL로 변환하여 메모리 부하 방지
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
        tmp.write(video_file.getvalue())
        tmp_path = tmp.name
    
    # 파일을 읽어오는 방식 대신 Streamlit의 정적 파일 경로 활용 (보안 우회)
    # 여기서는 가장 안정적인 Blob 주입 방식을 다시 사용하되 코드량을 최소화함
    import base64
    v_b64 = base64.b64encode(open(tmp_path, 'rb').read()).decode()
    os.unlink(tmp_path) # 사용 후 즉시 삭제

    return f"""
    <div style="width:100%; background:#000; border-radius:10px; overflow:hidden; position:relative;">
        <video id="v" controls playsinline style="width:100%; display:block; aspect-ratio:9/16;"></video>
        <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
        <div style="position:absolute; top:10px; right:10px; background:rgba(0,0,0,0.8); color:#0f0; padding:8px; border-radius:5px; font-family:monospace; z-index:1000; border:1px solid #0f0; font-size:16px;">
            Δ Spine: <span id="val">0.0</span>°
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const v=document.getElementById('v'), c=document.getElementById('c'), ctx=c.getContext('2d'), res=document.getElementById('val');
        let maxS=0, minS=180;
        const pose=new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:0, smoothLandmarks:true}}); // Complexity 0으로 낮춰 부하 최소화
        
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
            ctx.strokeStyle = '#00FF00'; ctx.lineWidth = 3;
            ctx.beginPath(); ctx.moveTo(sh.x*c.width, sh.y*c.height); ctx.lineTo(h.x*c.width, h.y*c.height); ctx.stroke();
        }});
        
        const blob = new Blob([Uint8Array.from(atob("{v_b64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}});
        v.src = URL.createObjectURL(blob);
        v.onplay = async () => {{ while(!v.paused && !v.ended){{ await pose.send({{image:v}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
    </script>
    """

# [3] 메인 레이아웃
f = st.file_uploader("영상을 업로드하세요", type=['mp4', 'mov'])

if f:
    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.subheader("🎥 고효율 분석기")
        components.html(get_light_engine(f), height=650)
    with c2:
        st.header("📋 AI 지능형 리포트")
        st.info("6월 탄생할 아기에게 보여줄 멋진 아빠의 스윙! 👶")
        s_val = st.number_input("위 분석기의 Δ Spine 값을 입력하세요", min_value=0.0, step=0.1)
        if s_val > 0 and st.button("🔄 Gemini 분석 시작"):
            with st.spinner("전문 역학 분석 중..."):
                prompt = f"척추각 편차 {s_val}도인 골퍼를 위해 운동학적 사슬 분석을 해주고 6월 아빠를 격려해줘."
                response = model.generate_content(prompt)
                st.chat_message("assistant").write(response.text)
                st.video("https://www.youtube.com/watch?v=VrOGGXdf_tM" if s_val > 4 else "https://www.youtube.com/watch?v=2vT64W2XfC0")

st.sidebar.markdown(f"**Baby Due: June 2026** 👶")
