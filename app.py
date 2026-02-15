import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import base64

# [1] Gemini 보안 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-pro') 
except Exception as e:
    st.error(f"Gemini API 인증 실패: {e}")
    st.stop()

st.set_page_config(layout="centered", page_title="GDR AI Final")
st.title("⛳ GDR AI Pro: 무결성 재생 버전 v23.0")

# [2] 하이퍼 안정화 엔진 (영상 로딩 최우선 구조)
def get_safe_engine(v_base64):
    return f"""
    <div id="container" style="width:100%; background:#000; border-radius:15px; overflow:hidden; position:relative;">
        <video id="v" controls playsinline style="width:100%; display:block; aspect-ratio:9/16; background:#000;"></video>
        <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
        <div id="hud" style="position:absolute; top:20px; right:20px; background:rgba(0,0,0,0.8); color:#0f0; padding:10px 15px; border-radius:8px; font-family:monospace; border:1px solid #0f0; z-index:1000; font-size:16px; display:none;">
            Δ Spine: <span id="val">0.0</span>°
        </div>
    </div>
    
    <script>
        const v=document.getElementById('v'), c=document.getElementById('c'), ctx=c.getContext('2d'), res=document.getElementById('val'), hud=document.getElementById('hud');
        let maxS=0, minS=180, pose=null;

        // 1. 영상 소스 주입 (Blob 방식으로 가장 가볍게)
        const b64Data = "{v_base64}";
        const byteCharacters = atob(b64Data);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {{ byteNumbers[i] = byteCharacters.charCodeAt(i); }}
        const blob = new Blob([new Uint8Array(byteNumbers)], {{type: 'video/mp4'}});
        v.src = URL.createObjectURL(blob);

        // 2. 영상이 로드된 후 AI 라이브러리를 동적으로 로드 (성공률 핵심)
        v.addEventListener('loadeddata', () => {{
            const script = document.createElement('script');
            script.src = "https://cdn.jsdelivr.net/npm/@mediapipe/pose";
            script.onload = () => {{
                pose = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` or `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
                pose.setOptions({{modelComplexity:1, smoothLandmarks:true}});
                pose.onResults((r) => {{
                    if(!r.poseLandmarks) return;
                    hud.style.display = 'block';
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
            }};
            document.head.appendChild(script);
        }});

        v.onplay = async () => {{ 
            if(pose) {{
                while(!v.paused && !v.ended) {{ 
                    await pose.send({{image:v}}); 
                    await new Promise(r=>requestAnimationFrame(r)); 
                }} 
            }}
        }};
    </script>
    """

# [3] UI 구성
f = st.file_uploader("스윙 영상을 업로드하세요", type=['mp4', 'mov'])

if f:
    v_base64 = base64.b64encode(f.read()).decode()
    components.html(get_safe_engine(v_base64), height=750)
    
    st.divider()
    
    # [4] AI 심층 역학 리포트 (사용자 입력 브릿지)
    st.header("📋 AI 지능형 역학 리포트")
    s_val = st.number_input("영상 우측 상단의 Δ Spine 수치를 입력하세요", min_value=0.0, step=0.1)
    
    if s_val > 0:
        if st.button("🔄 Gemini AI 분석 가동"):
            with st.spinner("전문 역학 분석 중..."):
                try:
                    prompt = f"척추각 편차 {s_val}도인 골퍼를 위해 운동학적 사슬 분석을 해주고 6월 아빠를 격려해줘."
                    response = model.generate_content(prompt)
                    st.chat_message("assistant").write(response.text)
                    st.video("https://www.youtube.com/watch?v=VrOGGXdf_tM" if s_val > 4 else "https://www.youtube.com/watch?v=2vT64W2XfC0")
                except Exception as e:
                    st.error(f"분석 오류: {e}")

st.sidebar.markdown(f"**Baby Due: June 2026** 👶")
