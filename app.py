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

st.set_page_config(layout="wide", page_title="GDR AI Pro v65")
st.title("⛳ GDR AI Pro: 데이터 래치 및 개별 초기화 v65.0")

# [2] 고정밀 역학 엔진 (트리거 로직 강화)
def get_latched_engine(f_v64, s_v64):
    return f"""
    <div style="display: flex; gap: 15px; background: #000; padding: 20px; border-radius: 12px; border: 1px solid #333;">
        <div style="flex: 1; position: relative; text-align: center;">
            <h4 style="color: #0f0;">FRONT (Peak Latch)</h4>
            <video id="vf" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div id="stats_f" style="margin-top:10px; background:rgba(0,255,0,0.1); color:#0f0; padding:12px; border-radius:8px; font-family:monospace; border:1px solid #0f0; font-size:14px;">
                Max Sway: <span id="f_sw_l">0.0</span>% | Max X-Factor: <span id="f_xf_l">0.0</span>°
            </div>
        </div>
        <div style="flex: 1; position: relative; text-align: center;">
            <h4 style="color: #0f0;">SIDE (Peak Latch)</h4>
            <video id="vs" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div id="stats_s" style="margin-top:10px; background:rgba(0,255,0,0.1); color:#0f0; padding:12px; border-radius:8px; font-family:monospace; border:1px solid #0f0; font-size:14px;">
                Max Δ Spine: <span id="s_sp_l">0.0</span>° | Max Knee: <span id="s_kn_l">0.0</span>°
            </div>
        </div>
    </div>
    <div style="text-align: center; margin-top: 15px;">
        <button onclick="copyData()" style="background:#0f0; color:#000; border:none; padding:12px 25px; border-radius:8px; cursor:pointer; font-weight:bold;">📋 통합 데이터 복사</button>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs');
        let f_refH=0, f_startCX=0, f_peakSw=0, f_maxXF=0, f_cnt=0, f_latched=false;
        let s_minS=0, s_maxS=0, s_peakSp=0, s_maxKn=0, s_latched=false, s_calibrated=false;

        // 개별 리셋 로직
        function resetFront() {{ f_refH=0; f_startCX=0; f_peakSw=0; f_maxXF=0; f_cnt=0; f_latched=false; document.getElementById('f_sw_l').innerText="0.0"; document.getElementById('f_xf_l').innerText="0.0"; }}
        function resetSide() {{ s_minS=0; s_maxS=0; s_peakSp=0; s_maxKn=0; s_latched=false; s_calibrated=false; document.getElementById('s_sp_l').innerText="0.0"; document.getElementById('s_kn_l').innerText="0.0"; }}

        function copyData() {{
            const data = `[ANALYSIS]\\nF_Sway: ${{document.getElementById('f_sw_l').innerText}}%\\nF_XFactor: ${{document.getElementById('f_xf_l').innerText}}deg\\nS_SpineDelta: ${{document.getElementById('s_sp_l').innerText}}deg\\nS_Knee: ${{document.getElementById('s_kn_l').innerText}}deg`;
            navigator.clipboard.writeText(data); alert("데이터가 복사되었습니다.");
        }}

        const poseF = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        const poseS = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        [poseF, poseS].forEach(p => p.setOptions({{modelComplexity:1, smoothLandmarks:true}}));

        poseF.onResults((r)=>{{
            if(!r.poseLandmarks || f_latched) return;
            const lm = r.poseLandmarks;
            const hL=lm[23], hR=lm[24], sL=lm[11], sR=lm[12];
            
            // 임팩트 래치: 손목이 골반 아래로 빠르게 내려가는 다운스윙 시점 감지 시 수치 고정
            if (lm[15].y > lm[23].y && lm[15].visibility > 0.8) {{ f_latched = true; return; }}

            if(f_cnt < 20) {{
                f_refH = (f_refH * f_cnt + Math.abs(hL.x - hR.x)) / (f_cnt + 1);
                f_startCX = (hL.x + hR.x) / 2;
                f_cnt++;
            }} else {{
                // Sway: 우측 이동(백스윙)만 측정
                const curSw = (( (hL.x + hR.x)/2 - f_startCX) / f_refH) * 100;
                if(curSw > f_peakSw && curSw < 22) f_peakSw = curSw;
                document.getElementById('f_sw_l').innerText = f_peakSw.toFixed(1);

                const curXF = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                if(curXF > f_maxXF && curXF < 68) f_maxXF = curXF;
                document.getElementById('f_xf_l').innerText = (f_maxXF * 1.1).toFixed(1); // 2D 왜곡 보정
            }}
        }});

        poseS.onResults((r)=>{{
            if(!r.poseLandmarks || s_latched) return;
            const lm = r.poseLandmarks;
            const hC = (lm[23].y + lm[24].y) / 2;
            const sC = (lm[11].y + lm[12].y) / 2;
            const curSp = Math.abs(Math.atan2(hC - sC, (lm[23].x + lm[24].x)/2 - (lm[11].x + lm[12].x)/2) * 180/Math.PI);

            // 측면 래치: 손목 위치로 임팩트 감지
            if (lm[15].y > lm[23].y) {{ s_latched = true; return; }}

            if(!s_calibrated) {{
                s_minS = curSp; s_maxS = curSp; s_calibrated = true;
            }} else {{
                if(curSp < s_minS) s_minS = curSp;
                if(curSp > s_maxS) s_maxS = curSp;
                let delta = s_maxS - s_minS;
                if(delta > s_peakSp && delta < 18) s_peakSp = delta;
                document.getElementById('s_sp_l').innerText = s_peakSp.toFixed(1);
            }}
            const curKn = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI);
            if(curKn > s_maxKn) s_maxKn = curKn;
            document.getElementById('s_kn_l').innerText = s_maxKn.toFixed(1);
        }});

        vf.onplay = () => {{ resetFront(); loopF(); }};
        vs.onplay = () => {{ resetSide(); loopS(); }};

        async function loopF() {{ while(!vf.paused){{ await poseF.send({{image:vf}}); await new Promise(r=>requestAnimationFrame(r)); }} }}
        async function loopS() {{ while(!vs.paused){{ await poseS.send({{image:vs}}); await new Promise(r=>requestAnimationFrame(r)); }} }}
        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
    </script>
    """

# [3] 파일 업로드 및 분석
c1, c2 = st.columns(2)
with c1: f_file = st.file_uploader("Front 영상", type=['mp4', 'mov'])
with c2: s_file = st.file_uploader("Side 영상", type=['mp4', 'mov'])

if f_file and s_file:
    f_b = base64.b64encode(f_file.read()).decode()
    s_b = base64.b64encode(s_file.read()).decode()
    components.html(get_latched_engine(f_b, s_b), height=600)

st.divider()
in_text = st.text_area("데이터를 붙여넣으세요.")

if st.button("🚀 정밀 분석 시작") and model:
    st.write(model.generate_content(f"역학 전문가로서 분석하십시오: {in_text}").text)
