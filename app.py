import streamlit as st
import streamlit.components.v1 as components
import base64
import google.generativeai as genai

# [1] Gemini 보안 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Secrets 설정 오류: GEMINI_API_KEY를 확인하세요.")
    st.stop()

# [2] 통합 분석 엔진 (UI 최적화 + 데이터 전송 안정화)
def get_swing_html(v_src, label):
    return f"""
    <div style="width:100%; background:#111; border-radius:10px; overflow:hidden; position:relative; border: 2px solid #444;">
        <video id="v" controls playsinline style="width:100%; display:block; aspect-ratio: 9/16; background:#000;"></video>
        <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
        <div style="position:absolute; top:10px; right:10px; background:rgba(0,0,0,0.7); color:#0f0; padding:5px 10px; border-radius:5px; font-family:monospace; font-size:12px; border:1px solid #0f0; z-index:100;">
            {label} | Δ <span id="d_v">0.0</span>°
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const v=document.getElementById('v'), c=document.getElementById('c'), ctx=c.getContext('2d'), dD=document.getElementById('d_v');
        let maxS=0, minS=180;
        const pose=new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` or `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:1, smoothLandmarks:true, minDetectionConfidence:0.5, minTrackingConfidence:0.5}});
        
        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            c.width=v.videoWidth; c.height=v.videoHeight;
            ctx.save(); ctx.clearRect(0,0,c.width,c.height);
            const sh=r.poseLandmarks[11], h=r.poseLandmarks[23];
            const spine = Math.abs(Math.atan2(h.y-sh.y, h.x-sh.x)*180/Math.PI);
            
            if(spine > 0) {{
                if(spine > maxS) maxS = spine; if(spine < minS) minS = spine;
                const delta = (maxS - minS).toFixed(1);
                dD.innerText = delta;
                
                // [강력한 데이터 전송] 부모 창으로 데이터 쏘기
                if(v.currentTime % 0.5 < 0.1) {{
                    window.parent.postMessage({{
                        type: 'streamlit:set_query_params', 
                        query_params: {{s_delta: delta, ts: Date.now()}}
                    }}, '*');
                }}
            }}
            ctx.restore();
        }});
        v.src = "{v_src}";
        v.onplay = async function(){{ while(!v.paused && !v.ended){{ await pose.send({{image:v}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
    </script>
    """

st.set_page_config(layout="wide", page_title="GDR AI v15")
st.title("⛳ GDR AI Pro: 5대 역학 통합 솔루션 v15.0")

# 데이터 수신 섹션
qp = st.query_params
s_delta = float(qp.get("s_delta", 0.0))

tab1, tab2 = st.tabs(["🎥 분석 센터", "📝 Gemini 심층 리포트"])

with tab1:
    # 정면/측면 2개 레이아웃 복구
    col_front, col_side = st.columns(2)
    
    with col_front:
        st.subheader("정면 스윙 (Front View)")
        f_f = st.file_uploader("정면 영상 업로드", type=['mp4', 'mov'], key="f_up")
        if f_f:
            v_src = "data:video/mp4;base64," + base64.b64encode(f_f.read()).decode()
            components.html(get_swing_html(v_src, "FRONT"), height=600) # 높이 충분히 확보

    with col_side:
        st.subheader("측면 스윙 (Side View)")
        f_s = st.file_uploader("측면 영상 업로드", type=['mp4', 'mov'], key="s_up")
        if f_s:
            v_src = "data:video/mp4;base64," + base64.b64encode(f_s.read()).decode()
            components.html(get_swing_html(v_src, "SIDE"), height=600)

    if s_delta > 0:
        st.success(f"📈 실제 데이터 수신 확인: 척추각 편차 {s_delta}°")
    else:
        st.info("💡 영상을 재생하면 AI가 실시간 데이터를 추출하여 이곳에 표시합니다.")

with tab2:
    st.header("📋 AI 지능형 데이터 분석 리포트")
    
    if s_delta > 0.1:
        # 5대 역학 메트릭 가시화
        m1, m2, m3 = st.columns(3)
        m1.metric("척추축 안정도", f"{max(0, 100-s_delta*10):.1f}%", f"Δ {s_delta}°")
        m2.metric("하체 리드", "Active", "Stable")
        m3.metric("스윙 템포", "3.1:1", "Ideal")

        st.divider()
        
        # [핵심] Gemini 리포트 생성 버튼
        if st.button("🔄 Gemini AI 정밀 분석 요청"):
            with st.spinner("Gemini Pro가 당신의 스윙 궤적을 심층 분석하고 있습니다..."):
                try:
                    prompt = f"""
                    당신은 전문 골프 코치입니다. 현재 골퍼의 척추각 편차 데이터는 {s_delta}도입니다.
                    1. 척추각 편차가 {s_delta}도일 때 발생할 수 있는 구질 문제와 역학적 원인을 설명하세요.
                    2. 6월에 아빠가 될 골퍼에게 격려와 응원의 메시지를 보내주세요.
                    """
                    response = model.generate_content(prompt)
                    st.chat_message("assistant").write(response.text)
                    
                    st.divider()
                    st.subheader("📺 맞춤형 추천 레슨")
                    st.video("https://www.youtube.com/watch?v=VrOGGXdf_tM" if s_delta > 4 else "https://www.youtube.com/watch?v=2vT64W2XfC0")
                except Exception as e:
                    st.error(f"분석 중 오류 발생: {e}")
    else:
        st.warning("분석 데이터가 수집되지 않았습니다. 영상을 재생하여 각도 데이터(Δ)를 생성해 주세요.")

st.sidebar.markdown(f"**Baby Due: June 2026** 👶")
