import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import base64

# [1] Gemini 보안 설정 (Secrets 기반)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # 모델명 NotFound 방지를 위해 gemini-pro 사용
    model = genai.GenerativeModel('gemini-pro') 
except Exception as e:
    st.error(f"Gemini API 인증 실패: {e}")
    st.stop()

st.set_page_config(layout="wide", page_title="GDR AI v32.0")
st.title("⛳ GDR AI Pro: 고정밀 역학 분석 v32.0")

# [2] 하이브리드 수치 안정화 엔진 (이동 평균 필터 탑재)
def get_pro_engine(v_b64):
    return f"""
    <div id="container" style="width:100%; background:#000; border-radius:15px; overflow:hidden; position:relative; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
        <video id="v" controls playsinline style="width:100%; display:block; aspect-ratio:9/16; background:#000;"></video>
        <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
        <div style="position:absolute; top:20px; right:20px; background:rgba(0,0,0,0.85); color:#0f0; padding:12px 18px; border-radius:10px; font-family:monospace; border:1px solid #0f0; z-index:1000; font-size:18px; box-shadow: 0 0 15px rgba(0,255,0,0.3);">
            Δ Spine (Filtered): <span id="val">0.0</span>°
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const v=document.getElementById('v'), c=document.getElementById('c'), ctx=c.getContext('2d'), res=document.getElementById('val');
        let maxS=0, minS=180;
        let angleHistory = []; // 데이터 보간 및 노이즈 필터링용 큐

        const pose=new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:1, smoothLandmarks:true, minDetectionConfidence:0.6}});
        
        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            c.width=v.videoWidth; c.height=v.videoHeight;
            ctx.clearRect(0,0,c.width,c.height);
            
            const sh=r.poseLandmarks[11], h=r.poseLandmarks[23];
            const currentAngle = Math.abs(Math.atan2(h.y-sh.y, h.x-sh.x)*180/Math.PI);

            // [보간 로직] 3프레임 이동 평균 필터 적용 (수치 변동성 제어)
            angleHistory.push(currentAngle);
            if(angleHistory.length > 3) angleHistory.shift();
            const filteredAngle = angleHistory.reduce((a,b)=>a+b)/angleHistory.length;

            if(filteredAngle > 0) {{
                if(filteredAngle > maxS) maxS = filteredAngle; 
                if(filteredAngle < minS) minS = filteredAngle;
                res.innerText = (maxS - minS).toFixed(1);
            }}
            
            // 척추 축 가시화 (데이터 수율 가독성 향상)
            ctx.strokeStyle = '#00FF00'; ctx.lineWidth = 5;
            ctx.lineCap = 'round';
            ctx.shadowBlur = 10; ctx.shadowColor = '#00FF00';
            ctx.beginPath(); 
            ctx.moveTo(sh.x*c.width, sh.y*c.height); 
            ctx.lineTo(h.x*c.width, h.y*c.height); 
            ctx.stroke();
        }});
        
        // Blob 방식을 통한 무결성 재생 보장
        const blob = new Blob([Uint8Array.from(atob("{v_b64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}});
        v.src = URL.createObjectURL(blob);
        
        v.onplay = async () => {{ 
            while(!v.paused && !v.ended){{ 
                await pose.send({{image:v}}); 
                await new Promise(r=>requestAnimationFrame(r)); 
            }} 
        }};
    </script>
    """

# [3] 메인 화면 구성
f = st.file_uploader("분석할 스윙 영상을 업로드하세요", type=['mp4', 'mov'])

if f:
    col_v, col_r = st.columns([1.3, 1])
    
    with col_v:
        st.subheader("🎥 실시간 역학 분석기 (Filtered)")
        v_b64 = base64.b64encode(f.read()).decode()
        components.html(get_pro_engine(v_b64), height=750)
        st.caption("※ 보간 필터가 적용되어 수치가 훨씬 안정적으로 출력됩니다.")

    with col_r:
        st.header("📋 AI 지능형 리포트")
        st.success("6월에 태어날 아기에게 보여줄 멋진 아빠의 스윙 분석! 👶")
        
        # 필터링된 수치를 입력받는 인터페이스
        s_val = st.number_input("위 분석기에서 확인된 Δ Spine 수치를 입력하세요", min_value=0.0, step=0.1)
        
        if s_val > 0:
            if st.button("🔄 Gemini AI 전문 분석 시작"):
                with st.spinner("전문 역학 데이터 해석 중..."):
                    try:
                        # 전문 역학 분석 프롬프트 고도화
                        prompt = f"""
                        당신은 골프 역학 전문가이자 코치입니다. 다음 데이터를 분석해주세요.
                        - 측정된 척추각 편차(Δ Spine): {s_val}도
                        
                        1. 이 데이터가 암시하는 '배치기(Early Extension)' 및 운동학적 사슬 문제를 원론적으로 분석하세요.
                        2. 지면 반력과 회전 축 유지 관점에서 개선해야 할 교정 방향을 제시하세요.
                        3. 6월에 아빠가 될 골퍼에게 따뜻한 격려를 한마디 덧붙여주세요.
                        한국어로 정중하고 전문적인 답변을 해주세요.
                        """
                        response = model.generate_content(prompt)
                        st.chat_message("assistant").write(response.text)
                        
                        st.divider()
                        st.subheader("📺 추천 교정 레슨")
                        yt_link = "https://www.youtube.com/watch?v=VrOGGXdf_tM" if s_val > 4 else "https://www.youtube.com/watch?v=2vT64W2XfC0"
                        st.video(yt_link)
                    except Exception as e:
                        st.error(f"리포트 생성 오류: {e}")
        else:
            st.info("영상을 재생하여 Δ Spine 수치를 확인한 뒤 위 칸에 입력해주세요.")

st.sidebar.markdown(f"**Baby Due: June 2026** 👶")
