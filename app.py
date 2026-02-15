import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import base64

# [1] 모델 초기화
def initialize_gemini():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return genai.GenerativeModel('models/gemini-1.5-flash')
    except: return None

model = initialize_gemini()

st.set_page_config(layout="wide", page_title="GDR AI Pro v63")
st.title("⛳ GDR AI Pro: 엔진 복구 및 안정화 v63.0")

# [2] 통합 안정화 엔진 (Impact Detection 감도 조정 및 인스턴스 최적화)
def get_stabilized_engine(f_v64, s_v64):
    return f"""
    <div style="display: flex; gap: 10px; background: #000; padding: 15px; border-radius: 12px; border: 1px solid #333;">
        <div style="flex: 1; position: relative; text-align: center;">
            <video id="vf" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div id="stats_f" style="margin-top:8px; color:#0f0; font-family:monospace; font-size:13px;">
                FRONT | Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°
            </div>
        </div>
        <div style="flex: 1; position: relative; text-align: center;">
            <video id="vs" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div id="stats_s" style="margin-top:8px; color:#0f0; font-family:monospace; font-size:13px;">
                SIDE | Δ Spine: <span id="s_sp">0.0</span>° | Knee: <span id="s_kn">0.0</span>°
            </div>
        </div>
    </div>
    <div style="text-align: center; margin-top: 15px;">
        <button onclick="copyData()" style="background:#0f0; color:#000; border:none; padding:10px 20px; border-radius:8px; cursor:pointer; font-weight:bold;">📋 통합 데이터 복사</button>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs');
        let f_refH=0, f_startCX=0, f_maxSw=0, f_maxXF=0, f_cnt=0;
        let s_minS=180, s_maxS=0, s_maxKn=0;

        function copyData() {{
            const data = `[STABILIZED_DATA]\\n` +
                         `FRONT_Sway: ${{document.getElementById('f_sw').innerText}}%\\n` +
                         `FRONT_XFactor: ${{document.getElementById('f_xf').innerText}}deg\\n` +
                         `SIDE_SpineDelta: ${{document.getElementById('s_sp').innerText}}deg\\n` +
                         `SIDE_Knee: ${{document.getElementById('s_kn').innerText}}deg`;
            navigator.clipboard.writeText(data);
            alert("안정화된 데이터가 복사되었습니다.");
        }}

        // 인스턴스 생성 시 메모리 부하 방지를 위해 modelComplexity 조정
        const poseF = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        const poseS = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        [poseF, poseS].forEach(p => p.setOptions({{modelComplexity:0, smoothLandmarks:true}}));

        poseF.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hL=lm[23], hR=lm[24], sL=lm[11], sR=lm[12];
            
            // 임팩트 셧다운 감도 완화 (영상이 바로 멈추는 것 방지)
            if (sR.x < hR.x - 0.15) return; 

            if(f_cnt < 15) {{
                f_refH = (f_refH * f_cnt + Math.abs(hL.x - hR.x)) / (f_cnt + 1);
                f_startCX = (hL.x + hR.x) / 2;
                f_cnt++;
            }} else {{
                const curSw = (( (hL.x + hR.x)/2 - f_startCX) / f_refH) * 100;
                if(curSw > f_maxSw && curSw < 20) f_maxSw = curSw;
                document.getElementById('f_sw').innerText = f_maxSw.toFixed(1);

                const curXF = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                if(curXF > f_maxXF && curXF < 70) f_maxXF = curXF;
                document.getElementById('f_xf').innerText = f_maxXF.toFixed(1);
            }}
        }});

        poseS.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hC = {{x:(lm[23].x+lm[24].x)/2, y:(lm[23].y+lm[24].y)/2}};
            const sC = {{x:(lm[11].x+lm[12].x)/2, y:(lm[11].y+lm[12].y)/2}};
            const curSp = Math.abs(Math.atan2(hC.y-sC.y, hC.x-sC.x)*180/Math.PI);
            
            if(curSp > 40 && curSp < 140) {{
                if(curSp < s_minS) s_minS = curSp;
                if(curSp > s_maxS) s_maxS = curSp;
                document.getElementById('s_sp').innerText = (s_maxS - s_minS).toFixed(1);
            }}
            const curKn = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI);
            if(curKn > s_maxKn) s_maxKn = curKn;
            document.getElementById('s_kn').innerText = s_maxKn.toFixed(1);
        }});

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        
        vf.onplay = async () => {{ while(!vf.paused){{ await poseF.send({{image:vf}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
        vs.onplay = async () => {{ while(!vs.paused){{ await poseS.send({{image:vs}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
    </script>
    """

# [3] 파일 업로드
c1, c2 = st.columns(2)
with c1: f_f = st.file_uploader("Front 영상", type=['mp4', 'mov'])
with c2: s_f = st.file_uploader("Side 영상", type=['mp4', 'mov'])

if f_f and s_f:
    components.html(get_stabilized_engine(base64.b64encode(f_f.read()).decode(), base64.b64encode(s_f.read()).decode()), height=550)

st.divider()
in_text = st.text_area("복사된 통합 데이터를 붙여넣으세요.")

if st.button("🚀 종합 분석 시작") and model:
    prompt = f"""당신은 역학 전문가입니다. 다음 데이터를 분석하여 기술적 진단을 수행하십시오. {in_text} 개인적 언급은 배제하십시오."""
    st.write(model.generate_content(prompt).text)
