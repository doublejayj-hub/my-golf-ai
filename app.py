import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import base64

# [1] Gemini 모델 자가 진단 및 할당 (최신 모델 고정)
def initialize_gemini():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # 가장 안정적인 호출 방식을 사용합니다.
        return genai.GenerativeModel('gemini-1.5-flash')
    except: return None

model = initialize_gemini()

st.set_page_config(layout="wide", page_title="GDR AI Engine v46")
st.title("⛳ GDR AI Pro: 무결성 재생 및 자동화 브릿지 v46.0")

# [2] 고도화된 역학 엔진 (Sway Ratio 정의 및 데이터 브릿지 포함)
def get_final_engine(v_b64, label):
    return f"""
    <div style="width:100%; background:#000; border-radius:12px; overflow:hidden; position:relative; border: 2px solid #333;">
        <video id="v" controls playsinline style="width:100%; display:block; aspect-ratio:9/16;"></video>
        <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
        <div id="stats" style="position:absolute; top:10px; right:10px; background:rgba(0,0,0,0.85); color:#0f0; padding:15px; border-radius:8px; font-family:monospace; border:1px solid #0f0; z-index:1000;">
            <b>[{label} DATA]</b><br>
            Sway Ratio: <span id="sw_v">0.0</span>%<br>
            Δ Spine: <span id="s_v">0.0</span>°<br>
            X-Factor: <span id="x_v">0.0</span>°
        </div>
        <button onclick="copyData()" style="position:absolute; bottom:10px; right:10px; z-index:1001; background:#0f0; color:#000; border:none; padding:5px 10px; border-radius:5px; cursor:pointer; font-weight:bold;">데이터 복사</button>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const v=document.getElementById('v'), c=document.getElementById('c'), ctx=c.getContext('2d');
        const sD=document.getElementById('s_v'), swD=document.getElementById('sw_v'), xD=document.getElementById('x_v');
        let minS=180, maxS=0, startX=0, angleHistory=[];

        function copyData() {{
            const data = `Sway: ${{swD.innerText}}%, Spine: ${{sD.innerText}}°, X: ${{xD.innerText}}°`;
            navigator.clipboard.writeText(data);
            alert("데이터가 클립보드에 복사되었습니다. 아래 입력창에 붙여넣으세요!");
        }}

        const pose=new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:1, smoothLandmarks:true}});
        
        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            c.width=v.videoWidth; c.height=v.videoHeight;
            ctx.clearRect(0,0,c.width,c.height);
            const lm = r.poseLandmarks;

            // 1. Sway Ratio (골반 너비 대비 이동 비율)
            const h_l = lm[23], h_r = lm[24];
            const hipWidth = Math.sqrt(Math.pow(h_l.x-h_r.x, 2) + Math.pow(h_l.y-h_r.y, 2));
            const h_c = {{x:(h_l.x+h_r.x)/2, y:(h_l.y+h_r.y)/2}};
            if(startX===0) startX = h_c.x;
            swD.innerText = ((Math.abs(h_c.x - startX) / hipWidth) * 100).toFixed(1);

            // 2. Δ Spine (척추축 안정도)
            const sh_c = {{x:(lm[11].x+lm[12].x)/2, y:(lm[11].y+lm[12].y)/2}};
            const curA = Math.abs(Math.atan2(h_c.y-sh_c.y, h_c.x-sh_c.x)*180/Math.PI);
            angleHistory.push(curA); if(angleHistory.length>3) angleHistory.shift();
            const fA = angleHistory.reduce((a,b)=>a+b)/angleHistory.length;
            if(fA<minS) minS=fA; if(fA>maxS) maxS=fA;
            sD.innerText = (maxS-minS).toFixed(1);

            // 3. X-Factor (상하체 회전 분리)
            const shRot = Math.atan2(lm[12].y-lm[11].y, lm[12].x-lm[11].x)*180/Math.PI;
            const hRot = Math.atan2(lm[24].y-lm[23].y, lm[24].x-lm[23].x)*180/Math.PI;
            xD.innerText = Math.abs(shRot - hRot).toFixed(1);

            ctx.strokeStyle = '#00FF00'; ctx.lineWidth = 3;
            ctx.beginPath(); ctx.moveTo(sh_c.x*c.width, sh_c.y*c.height); ctx.lineTo(h_c.x*c.width, h_c.y*c.height); ctx.stroke();
        }});
        
        const blob = new Blob([Uint8Array.from(atob("{v_b64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}});
        v.src = URL.createObjectURL(blob);
        v.onplay = async () => {{ while(!v.paused && !v.ended){{ await pose.send({{image:v}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
    </script>
    """

# [3] UI 및 리포트 섹션
f_front = st.sidebar.file_uploader("정면 영상", type=['mp4', 'mov'])
if f_front:
    v_b64 = base64.b64encode(f_front.read()).decode()
    components.html(get_final_engine(v_b64, "FRONT"), height=650)

st.divider()

# [4] 제미나이 통합 분석 (Sway Ratio 정의 포함)
st.header("🔬 데이터 통합 기술 진단")
in_data = st.text_area("영상 분석기의 '데이터 복사' 버튼을 누른 후 여기에 붙여넣으세요.")

if st.button("🚀 제미나이 리포트 생성") and model:
    with st.spinner("물리 데이터 정의에 기반하여 분석 중..."):
        prompt = f"""
        당신은 물리 데이터 기반 골프 역학 전문가입니다.
        [수치 정의]
        - Sway Ratio: 골반 너비를 100%로 보았을 때의 수평 이동 비율입니다.
        - Δ Spine: 척추 각도의 최대 변화량(Stable vs Early Extension)입니다.
        
        [사용자 데이터]
        {in_data}
        
        위 수치들을 바탕으로 스윙의 물리적 안정성과 개선 방안을 기술적으로 분석하십시오.
        """
        response = model.generate_content(prompt)
        st.write(response.text)
