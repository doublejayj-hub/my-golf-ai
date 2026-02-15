import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import base64

# [1] 모델 자동 탐색 및 할당 (최신 안정화 버전)
def get_working_model():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for target in ['models/gemini-1.5-flash', 'models/gemini-pro']:
            if target in models: return genai.GenerativeModel(target)
        return genai.GenerativeModel(models[0]) if models else None
    except: return None

model = get_working_model()

st.set_page_config(layout="wide", page_title="GDR AI Engine v51")
st.title("⛳ GDR AI Pro: 데이터 인식 무결성 버전 v51.0")

# [2] 정밀 역학 엔진 (데이터 태깅 강화)
def get_expert_engine(v_b64, mode):
    label = "FRONT" if "정면" in mode else "SIDE"
    return f"""
    <div style="width:100%; background:#000; border-radius:12px; overflow:hidden; position:relative; border: 2px solid #333;">
        <video id="v" controls playsinline style="width:100%; display:block; aspect-ratio:9/16; background:#000;"></video>
        <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
        <div id="stats" style="position:absolute; top:10px; right:10px; background:rgba(0,0,0,0.85); color:#0f0; padding:15px; border-radius:8px; font-family:monospace; border:1px solid #0f0; z-index:1000; font-size:12px;">
            <b style="color:#fff;">[{label} VIEW]</b><br>
            Δ Spine: <span id="s_v">0.0</span>°<br>
            Sway Ratio: <span id="sw_v">0.0</span>%<br>
            X-Factor: <span id="x_v">0.0</span>°<br>
            Knee Angle: <span id="k_v">0.0</span>°
        </div>
        <button onclick="copyData()" style="position:absolute; bottom:15px; right:15px; z-index:1001; background:#0f0; color:#000; border:none; padding:10px 15px; border-radius:5px; cursor:pointer; font-weight:bold;">📋 수치 복사</button>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const v=document.getElementById('v'), c=document.getElementById('c'), ctx=c.getContext('2d');
        const sD=document.getElementById('s_v'), swD=document.getElementById('sw_v'), xD=document.getElementById('x_v'), kD=document.getElementById('k_v');
        let minS=180, maxS=0, startX=0, angleHistory=[];

        // [핵심] 제미나이가 인식하기 쉬운 태그형 데이터로 복사
        function copyData() {{
            const dataStr = `[ANALYSIS_DATA]
VIEW: {label}
SWAY_RATIO: ${{swD.innerText}}%
SPINE_DELTA: ${{sD.innerText}}deg
X_FACTOR: ${{xD.innerText}}deg
KNEE_ANGLE: ${{kD.innerText}}deg`;
            
            navigator.clipboard.writeText(dataStr).then(() => {{
                alert(`${label} 역학 데이터가 표준 포맷으로 복사되었습니다.`);
            }});
        }}

        const pose=new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:1, smoothLandmarks:true}});
        
        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            c.width=v.videoWidth; c.height=v.videoHeight;
            ctx.clearRect(0,0,c.width,c.height);
            const lm = r.poseLandmarks;
            const h_l=lm[23], h_r=lm[24], sh_l=lm[11], sh_r=lm[12];
            const hipW = Math.sqrt(Math.pow(h_l.x-h_r.x,2)+Math.pow(h_l.y-h_r.y,2));
            const h_c = {{x:(h_l.x+h_r.x)/2, y:(h_l.y+h_r.y)/2}};
            const sh_c = {{x:(sh_l.x+sh_r.x)/2, y:(sh_l.y+sh_r.y)/2}};

            // 역학 연산 및 필터링 (기존 무결성 로직 유지)
            const curA = Math.abs(Math.atan2(h_c.y-sh_c.y, h_c.x-sh_c.x)*180/Math.PI);
            angleHistory.push(curA); if(angleHistory.length>3) angleHistory.shift();
            const fA = angleHistory.reduce((a,b)=>a+b)/angleHistory.length;
            if(fA<minS) minS=fA; if(fA>maxS) maxS=fA;
            sD.innerText = (maxS-minS).toFixed(1);

            if(startX===0) startX = h_c.x;
            swD.innerText = ((Math.abs(h_c.x - startX) / hipW) * 100).toFixed(1);

            const shRot = Math.atan2(sh_r.y-sh_l.y, sh_r.x-sh_l.x)*180/Math.PI;
            const hRot = Math.atan2(h_r.y-h_l.y, h_r.x-h_l.x)*180/Math.PI;
            xD.innerText = Math.abs(shRot - hRot).toFixed(1);
            kD.innerText = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI).toFixed(1);

            ctx.strokeStyle = '#00FF00'; ctx.lineWidth = 4;
            ctx.beginPath(); ctx.moveTo(sh_c.x*c.width, sh_c.y*c.height); ctx.lineTo(h_c.x*c.width, h_c.y*c.height); ctx.stroke();
        }});
        
        const blob = new Blob([Uint8Array.from(atob("{v_b64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}});
        v.src = URL.createObjectURL(blob);
        v.onplay = async () => {{ while(!v.paused && !v.ended){{ await pose.send({{image:v}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
    </script>
    """

# [3] 파일 업로드 및 분석기 레이아웃
view_mode = st.sidebar.radio("분석 시점 선택", ("정면 (Front View)", "측면 (Side View)"))
f = st.file_uploader(f"{view_mode} 영상을 업로드하세요", type=['mp4', 'mov'])
if f:
    v_b64 = base64.b64encode(f.read()).decode()
    components.html(get_expert_engine(v_b64, view_mode), height=700)

st.divider()

# [4] 제미나이 통합 리포트 (X-Factor 정의 및 개인화 배제)
st.header("🔬 기술 데이터 기반 역학 리포트")
in_text = st.text_area("영상 분석기의 '수치 복사' 버튼을 누른 후 여기에 붙여넣으십시오.")

if st.button("🚀 정밀 분석 시작") and model:
    with st.spinner("전문 모델이 물리 지표를 해석 중입니다..."):
        prompt = f"""
        당신은 물리 데이터 기반 골프 역학 전문가입니다. 다음 수치 정의를 엄격히 준수하여 분석하십시오.
        
        [지표 정의 가이드]
        - X_FACTOR: 상체(어깨)와 하체(골반)의 회전 각도 차이입니다. 꼬임 에너지의 척도입니다.
        - SPINE_DELTA: 척추축의 안정성 지표입니다. (Stable: < 4deg)
        - SWAY_RATIO: 골반 너비 대비 수평 이동 비율입니다.
        
        [입력 데이터]
        {in_text}
        
        위 데이터를 바탕으로 사용자의 스윙 궤적과 회전 효율을 물리적 관점에서 진단하십시오. 
        개인적인 언급이나 격려는 모두 생략하고, 오직 기술적 개선 방안과 물리적 인과관계만 서술하십시오.
        """
        response = model.generate_content(prompt)
        st.info(f"분석 결과 (엔진: {model.model_name})")
        st.write(response.text)
