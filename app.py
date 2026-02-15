import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import base64

# [1] Gemini 모델 초기화
def initialize_gemini():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return genai.GenerativeModel('models/gemini-1.5-flash')
    except: return None

model = initialize_gemini()

st.set_page_config(layout="wide", page_title="GDR AI Pro v64")
st.title("⛳ GDR AI Pro: 자동 리셋 및 역학 고도화 v64.0")

# [2] 자동 리셋 기능이 탑재된 통합 엔진
def get_auto_reset_engine(f_v64, s_v64):
    return f"""
    <div style="display: flex; gap: 15px; background: #000; padding: 20px; border-radius: 12px; border: 1px solid #333;">
        <div style="flex: 1; position: relative; text-align: center;">
            <h4 style="color: #0f0;">FRONT (Peak Locked)</h4>
            <video id="vf" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div id="stats_f" style="margin-top:10px; background:rgba(0,255,0,0.1); color:#0f0; padding:12px; border-radius:8px; font-family:monospace; border:1px solid #0f0; font-size:14px;">
                Max Sway: <span id="f_sw_l">0.0</span>% | Max X-Factor: <span id="f_xf_l">0.0</span>°
            </div>
        </div>
        <div style="flex: 1; position: relative; text-align: center;">
            <h4 style="color: #0f0;">SIDE (Peak Locked)</h4>
            <video id="vs" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div id="stats_s" style="margin-top:10px; background:rgba(0,255,0,0.1); color:#0f0; padding:12px; border-radius:8px; font-family:monospace; border:1px solid #0f0; font-size:14px;">
                Max Δ Spine: <span id="s_sp_l">0.0</span>° | Max Knee: <span id="s_kn_l">0.0</span>°
            </div>
        </div>
    </div>
    <div style="text-align: center; margin-top: 20px;">
        <button onclick="copyLockedData()" style="background:#0f0; color:#000; border:none; padding:15px 30px; border-radius:10px; cursor:pointer; font-weight:bold; font-size:16px;">📋 정점 데이터 복사 및 리셋</button>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs');
        let f_refH=0, f_startCX=0, f_maxSw=0, f_maxXF=0, f_cnt=0;
        let s_minS=180, s_maxS=0, s_peakSp=0, s_maxKn=0;

        // [핵심] 수치 초기화 함수
        function resetStats() {{
            f_refH=0; f_startCX=0; f_maxSw=0; f_maxXF=0; f_cnt=0;
            s_minS=180; s_maxS=0; s_peakSp=0; s_maxKn=0;
            document.getElementById('f_sw_l').innerText = "0.0";
            document.getElementById('f_xf_l').innerText = "0.0";
            document.getElementById('s_sp_l').innerText = "0.0";
            document.getElementById('s_kn_l').innerText = "0.0";
            console.log("Stats Reset Completed");
        }}

        function copyLockedData() {{
            const data = `[PEAK_LOCKED_DATA]\\n` +
                         `FRONT_Max_Sway: ${{document.getElementById('f_sw_l').innerText}}%\\n` +
                         `FRONT_Max_XFactor: ${{document.getElementById('f_xf_l').innerText}}deg\\n` +
                         `SIDE_Max_SpineDelta: ${{document.getElementById('s_sp_l').innerText}}deg\\n` +
                         `SIDE_Max_Knee: ${{document.getElementById('s_kn_l').innerText}}deg`;
            navigator.clipboard.writeText(data);
            alert("정점 데이터가 복사되었습니다.");
        }}

        const poseF = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        const poseS = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        [poseF, poseS].forEach(p => p.setOptions({{modelComplexity:1, smoothLandmarks:true}}));

        // 정면 처리 (X-Factor 1.2배 보정 및 Sway 범위 제한)
        poseF.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hL=lm[23], hR=lm[24], sL=lm[11], sR=lm[12];
            
            if(f_cnt < 20) {{
                f_refH = (f_refH * f_cnt + Math.abs(hL.x - hR.x)) / (f_cnt + 1);
                f_startCX = (hL.x + hR.x) / 2;
                f_cnt++;
            }} else {{
                const curSw = (( (hL.x + hR.x)/2 - f_startCX) / f_refH) * 100;
                if(curSw > f_maxSw && curSw < 20) f_maxSw = curSw; 
                document.getElementById('f_sw_l').innerText = f_maxSw.toFixed(1);

                const sRot = Math.atan2(sR.y-sL.y, sR.x-sL.x) * 180/Math.PI;
                const hRot = Math.atan2(hR.y-hL.y, hR.x-hR.y) * 180/Math.PI;
                let curXF = Math.abs(sRot - hRot) * 1.2; 
                if(curXF > f_maxXF && curXF < 65) f_maxXF = curXF;
                document.getElementById('f_xf_l').innerText = f_maxXF.toFixed(1);
            }}
        }});

        // 측면 처리
        poseS.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hC = {{x:(lm[23].x+lm[24].x)/2, y:(lm[23].y+lm[24].y)/2}};
            const sC = {{x:(lm[11].x+lm[12].x)/2, y:(lm[11].y+lm[12].y)/2}};
            const curSp = Math.abs(Math.atan2(hC.y-sC.y, hC.x-sC.x)*180/Math.PI);
            
            if(curSp > 45 && curSp < 135) {{
                if(curSp < s_minS) s_minS = curSp;
                if(curSp > s_maxS) s_maxS = curSp;
                const delta = s_maxS - s_minS;
                if(delta > s_peakSp && delta < 15) s_peakSp = delta;
                document.getElementById('s_sp_l').innerText = s_peakSp.toFixed(1);
            }}
            const curKn = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI);
            if(curKn > s_maxKn) s_maxKn = curKn;
            document.getElementById('s_kn_l').innerText = s_maxKn.toFixed(1);
        }});

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        
        // 재생 시 자동 리셋 트리거
        vf.onplay = () => {{ resetStats(); loopF(); }};
        vs.onplay = () => {{ loopS(); }};

        async function loopF() {{ while(!vf.paused){{ await poseF.send({{image:vf}}); await new Promise(r=>requestAnimationFrame(r)); }} }}
        async function loopS() {{ while(!vs.paused){{ await poseS.send({{image:vs}}); await new Promise(r=>requestAnimationFrame(r)); }} }}
    </script>
    """

# [3] 파일 업로드
c1, c2 = st.columns(2)
with c1: f_f = st.file_uploader("정면 영상", type=['mp4', 'mov'])
with c2: s_f = st.file_uploader("측면 영상", type=['mp4', 'mov'])

if f_f and s_f:
    f_b64 = base64.b64encode(f_f.read()).decode()
    s_b64 = base64.b64encode(s_f.read()).decode()
    components.html(get_auto_reset_engine(f_b64, s_b64), height=600)

st.divider()
in_text = st.text_area("Peak-Locked 데이터를 여기에 붙여넣으세요.")

if st.button("🚀 종합 역학 분석 시작") and model:
    prompt = f"""
    운동역학 전문가로서 분석하십시오.
    [정규화 수치] {in_text}
    기술적 관점에서 비거리와 정타율 개선안을 제시하십시오.
    """
    st.write(model.generate_content(prompt).text)
