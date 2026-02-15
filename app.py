import streamlit as st
import google.generativeai as genai
import base64

# [1] Gemini 보안 설정 (Secrets 기반)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception:
    st.error("Gemini API 키 설정을 확인해주세요.")
    st.stop()

st.set_page_config(layout="centered")
st.title("⛳ GDR AI Pro v19.0 (재생 무결성 버전)")

# [2] 비디오 업로드 및 처리를 위한 가벼운 로직
f = st.file_uploader("영상을 선택하세요", type=['mp4', 'mov'])

if f:
    # 파일을 Base64로 변환 (가장 원시적인 방식 사용)
    t = base64.b64encode(f.read()).decode()
    v_url = f"data:video/mp4;base64,{t}"

    # [핵심] HTML/JS 엔진 분리: 비디오 로딩 후 분석기 가동
    # f-string 대신 수동 replace를 사용하여 중괄호 충돌 방지
    raw_html = """
    <div style="width:100%; background:#000; border-radius:15px; position:relative;">
        <video id="vid" controls playsinline style="width:100%; border-radius:15px;"></video>
        <canvas id="out" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
        <div style="position:absolute; top:10px; right:10px; background:rgba(0,0,0,0.8); color:#0f0; padding:8px; border:1px solid #0f0; border-radius:5px; font-family:monospace; z-index:999;">
            Δ Spine: <span id="deg">0.0</span>°
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const v = document.getElementById('vid');
        const c = document.getElementById('out');
        const ctx = c.getContext('2d');
        const d = document.getElementById('deg');
        let mx=0, mi=180;

        // 1. 모델 준비
        const pose = new Pose({locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${p}`});
        pose.setOptions({modelComplexity: 1, smoothLandmarks: true});
        pose.onResults((r) => {
            if(!r.poseLandmarks) return;
            c.width = v.videoWidth; c.height = v.videoHeight;
            ctx.clearRect(0,0,c.width,c.height);
            const sh = r.poseLandmarks[11], h = r.poseLandmarks[23];
            const ang = Math.abs(Math.atan2(h.y-sh.y, h.x-sh.x)*180/Math.PI);
            if(ang > 0) {
                if(ang > mx) mx = ang; if(ang < mi) mi = ang;
                d.innerText = (mx - mi).toFixed(1);
            }
            // 뼈대 그리기 (최소화)
            ctx.strokeStyle = '#00FF00'; ctx.lineWidth = 2;
            ctx.beginPath(); ctx.moveTo(sh.x*c.width, sh.y*c.height); ctx.lineTo(h.x*c.width, h.y*c.height); ctx.stroke();
        });

        // 2. 비디오 소스 주입 및 재생 보장
        v.src = "VIDEO_PLACEHOLDER";
        v.onloadedmetadata = () => {
            v.onplay = async () => {
                while(!v.paused && !v.ended) {
                    await pose.send({image: v});
                    await new Promise(r => requestAnimationFrame(r));
                }
            };
        };
    </script>
    """
    st.components.v1.html(raw_html.replace("VIDEO_PLACEHOLDER", v_url), height=600)

    st.divider()

    # [3] 리포트 섹션: 6월 아빠를 위한 심층 진단
    st.header("📋 AI 역학 정밀 리포트")
    val = st.number_input("위 영상의 Δ Spine 수치를 입력하세요", min_value=0.0, step=0.1)
    
    if val > 0:
        if st.button("🔄 Gemini AI 분석 시작"):
            with st.spinner("전문 역학 분석 중..."):
                prompt = f"척추각 편차 {val}도인 골퍼에게 6월 탄생할 아기를 언급하며 전문적인 골프 역학 조언을 해줘."
                response = model.generate_content(prompt)
                st.chat_message("assistant").write(response.text)
                st.video("https://www.youtube.com/watch?v=VrOGGXdf_tM" if val > 4 else "https://www.youtube.com/watch?v=2vT64W2XfC0")
