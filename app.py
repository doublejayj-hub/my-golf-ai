import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import base64

# [1] 모델 자동 탐색 및 강제 할당 로직
def get_working_model():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # 현재 API 키로 사용 가능한 모든 모델 리스트를 직접 가져옵니다.
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 선호 모델 순서대로 탐색 (Flash -> Pro -> 기타)
        target_models = ['models/gemini-1.5-flash', 'models/gemini-pro', 'models/gemini-1.5-flash-latest']
        for target in target_models:
            if target in models:
                return genai.GenerativeModel(target)
        
        # 위 모델들이 없으면 목록 중 첫 번째 모델이라도 강제로 연결
        if models:
            return genai.GenerativeModel(models[0])
        return None
    except Exception as e:
        st.error(f"모델 연결 중 치명적 오류: {e}")
        return None

# 전역 모델 변수 할당
model = get_working_model()

st.set_page_config(layout="wide", page_title="GDR AI Engine v47")
st.title("⛳ GDR AI Pro: 모델 경로 자동 복구 버전 v47.0")

# [2] 정밀 역학 엔진 (재생 무결성 유지)
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
        <button onclick="copyData()" style="position:absolute; bottom:10px; right:10px; z-index:1001; background:#0f0; color:#000; border:none; padding:8px 12px; border-radius:5px; cursor:pointer; font-weight:bold;">📋 수치 복사</button>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const v=document.getElementById('v'), c=document.getElementById('c'), ctx=c.getContext('2d');
        const sD=document.getElementById('s_v'), swD=document.getElementById('sw_v'), xD=document.getElementById('x_v');
        let minS=180, maxS=0, startX=0, angleHistory=[];

        function copyData() {{
            const data = `Sway: ${{swD.innerText}}%, Spine: ${{sD.innerText}}°, X: ${{xD.innerText}}°`;
            navigator.clipboard.writeText(data);
            alert("수치가 복사되었습니다! 아래 입력창에 붙여넣어 주세요.");
        }}

        const pose=new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:1, smoothLandmarks:true}});
        
        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            c.width=v.videoWidth; c.height=v.videoHeight;
            ctx.clearRect(0,0,c.width,c.height);
            const lm = r.poseLandmarks;
            const h_l = lm[23], h_r = lm[24], sh_l = lm[11], sh_r = lm[12];
            const hipWidth = Math.sqrt(Math.pow(h_l.x-h_r.x, 2) + Math.pow(h_l.y-h_r.y, 2));
            const h_c = {{x:(h_l.x+h_r.x)/2, y:(h_l.y+h_r.y)/2}};
            const sh_c = {{x:(sh_l.x+sh_r.x)/2, y:(sh_l.y+sh_r.y)/2}};

            if(startX===0) startX = h_c.x;
            swD.innerText = ((Math.abs(h_c.x - startX) / hipWidth) * 100).toFixed(1);
            const curA = Math.abs(Math.atan2(h_c.y-sh_c.y, h_c.x-sh_c.x)*180/Math.PI);
            angleHistory.push(curA); if(angleHistory.length>3) angleHistory.shift();
            const fA = angleHistory.reduce((a,b)=>a+b)/angleHistory.length;
            if(fA<minS) minS=fA; if(fA>maxS) maxS=fA;
            sD.innerText = (maxS-minS).toFixed(1);
            const shRot = Math.atan2(sh_r.y-sh_l.y, sh_r.x-sh_l.x)*180/Math.PI;
            const hRot = Math.atan2(h_r.y-h_l.y, h_r.x-h_l.x)*180/Math.PI;
            xD.innerText = Math.abs(shRot - hRot).toFixed(1);

            ctx.strokeStyle = '#00FF00'; ctx.lineWidth = 4;
            ctx.beginPath(); ctx.moveTo(sh_c.x*c.width, sh_c.y*c.height); ctx.lineTo(h_c.x*c.width, h_c.y*c.height); ctx.stroke();
        }});
        
        const blob = new Blob([Uint8Array.from(atob("{v_b64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}});
        v.src = URL.createObjectURL(blob);
        v.onplay = async () => {{ while(!v.paused && !v.ended){{ await pose.send({{image:v}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
    </script>
    """

# [3] 파일 업로드 및 분석기 레이아웃
f_input = st.sidebar.file_uploader("스윙 영상을 업로드하세요", type=['mp4', 'mov'])
if f_input:
    v_b64 = base64.b64encode(f_input.read()).decode()
    components.html(get_final_engine(v_b64, "SWING"), height=650)

st.divider()

# [4] 물리 정의 기반 통합 분석 리포트
st.header("🔬 데이터 기술 통합 리포트")
in_text = st.text_area("영상에서 복사한 데이터를 여기에 붙여넣으세요.")

if st.button("🚀 전문 리포트 생성") and model:
    with st.spinner("서버에서 사용 가능한 최적 모델로 분석 중..."):
        prompt = f"""
        당신은 물리 데이터 기반 골프 역학 전문가입니다.
        [수치 정의 가이드]
        - Sway Ratio: 골반 너비를 100%로 보았을 때의 수평 이동 비율입니다.
        - Δ Spine: 척추 각도의 최대 변화 범위입니다. (Stable: < 4°)
        
        [사용자 데이터]
        {in_text}
        
        위 수치들을 바탕으로 척추축 안정성과 에너지 전달 효율을 물리적 관점에서 정밀 분석하십시오.
        불필요한 미사여구는 배제하십시오.
        """
        try:
            response = model.generate_content(prompt)
            st.success(f"분석 완료 (사용 모델: {model.model_name})")
            st.write(response.text)
        except Exception as e:
            st.error(f"리포트 생성 실패: {e}")
