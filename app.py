import streamlit as st
import streamlit.components.v1 as components
import base64
import google.generativeai as genai

# [1] 보안 연동: Secrets에서 API 키 호출
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("API 키가 설정되지 않았습니다. Streamlit Cloud의 Secrets 설정을 확인해주세요.")
    st.stop()

# [2] 고성능 물리 추출 엔진 (하이퍼 보간 및 실시간 전송)
def get_final_engine_html(v_src, label):
    return f"""
    <div style="width:100%; background:#000; border-radius:12px; overflow:hidden; position:relative;">
        <video id="v" controls playsinline style="width:100%; display:block; height:auto;"></video>
        <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
        <div style="position:absolute; bottom:50px; left:0; width:100%; background:rgba(0,0,0,0.7); color:#0f0; padding:8px 15px; font-family:monospace; z-index:100; display:flex; justify-content:space-between; font-size:13px; border-top:1px solid #0f0;">
            <span>VIEW: {label}</span>
            <span>SPINE: <b id="s_v">0.0</b>°</span>
            <span id="md" style="color:#ff0;">STD</span>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils"></script>
    <script>
        const v=document.getElementById('v'), c=document.getElementById('c'), ctx=c.getContext('2d'), sD=document.getElementById('s_v');
        let maxS=0, minS=180, pL=null, pY=0;
        const pose=new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` or `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:1, smoothLandmarks:true, minDetectionConfidence:0.5, minTrackingConfidence:0.5}});
        
        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            c.width=v.videoWidth; c.height=v.videoHeight;
            ctx.save(); ctx.clearRect(0,0,c.width,c.height);
            const sh=r.poseLandmarks[11], h=r.poseLandmarks[23], w=r.poseLandmarks[15];
            const spine = Math.abs(Math.atan2(h.y-sh.y, h.x-sh.x)*180/Math.PI);
            if(spine > maxS) maxS = spine; if(spine < minS) minS = spine;
            sD.innerText = spine.toFixed(1);

            if(v.currentTime > 1 && v.currentTime % 2 < 0.1) {{
                window.parent.postMessage({{
                    type: 'streamlit:set_query_params', 
                    query_params: {{s_delta: (maxS-minS).toFixed(1)}}
                }}, '*');
            }}
            drawConnectors(ctx,r.poseLandmarks,POSE_CONNECTIONS,{{color:'#00FF00',lineWidth:3}});
            ctx.restore();
        }});
        v.src = "{v_src}";
        v.onplay = async function(){{ while(!v.paused && !v.ended){{ await pose.send({{image:v}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
    </script>
    """

st.set_page_config(layout="wide", page_title="GDR AI Pro v12.0")
st.title("⛳ Gemini Pro 지능형 골프 대시보드")

# 실시간 분석 데이터 수신
qp = st.query_params
s_delta = float(qp.get("s_delta", 0.0))

tab1, tab2 = st.tabs(["🎥 분석 센터", "🤖 Gemini 심층 리포트"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        f_f = st.file_uploader("정면 업로드", type=['mp4', 'mov'], key="f")
        if f_f:
            v_src = "data:video/mp4;base64," + base64.b64encode(f_f.read()).decode()
            components.html(get_final_engine_html(v_src, "FRONT"), height=450)
    with c2:
        f_s = st.file_uploader("측면 업로드", type=['mp4', 'mov'], key="s")
        if f_s:
            v_src = "data:video/mp4;base64," + base64.b64encode(f_s.read()).decode()
            components.html(get_final_engine_html(v_src, "SIDE"), height=450)

with tab2:
    st.header("📋 AI 실시간 역학 분석 (Powered by Gemini)")
    if s_delta > 0:
        with st.spinner("Gemini Pro가 실제 데이터를 분석 중입니다..."):
            prompt = f"척추각 편차 {s_delta}도인 골퍼에게 6월 탄생할 아기를 언급하며 전문적인 골프 역학 조언을 해줘."
            response = model.generate_content(prompt)
            st.chat_message("assistant").write(response.text)
            
        st.divider()
        st.subheader("📸 프로 레퍼런스 가이드")
        st.image("https://img.vavel.com/tiger-woods-swing-1608144214553.jpg", caption="Tiger Woods의 완벽한 척추각 유지")
    else:
        st.info("영상을 재생하면 실제 데이터 기반 리포트가 생성됩니다.")

st.sidebar.markdown(f"**Baby Due: June 2026** 👶")
