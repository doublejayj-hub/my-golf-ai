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

st.set_page_config(layout="wide", page_title="GDR AI Pro v68")
st.title("⛳ GDR AI Pro: 초정밀 임팩트 래치 패치 v68.0")

# [2] 고정밀 역학 엔진 (물리적 잠금 강화)
def get_final_engine(f_v64, s_v64):
    return f"""
    <div style="display: flex; gap: 15px; background: #000; padding: 20px; border-radius: 12px; border: 1px solid #333;">
        <div style="flex: 1; position: relative; text-align: center;">
            <h4 style="color: #0f0;">FRONT (Hard Locked)</h4>
            <video id="vf" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div id="stats_f" style="margin-top:10px; background:rgba(0,255,0,0.1); color:#0f0; padding:12px; border-radius:8px; font-family:monospace; border:1px solid #0f0; font-size:16px;">
                Sway: <span id="f_sw_l">0.0</span>% | X-Factor: <span id="f_xf_l">0.0</span>°
            </div>
        </div>
        <div style="flex: 1; position: relative; text-align: center;">
            <h4 style="color: #0f0;">SIDE (Hard Locked)</h4>
            <video id="vs" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div id="stats_s" style="margin-top:10px; background:rgba(0,255,0,0.1); color:#0f0; padding:12px; border-radius:8px; font-family:monospace; border:1px solid #0f0; font-size:16px;">
                Δ Spine: <span id="s_sp_l">0.0</span>° | Knee: <span id="s_kn_l">0.0</span>°
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs');
        let f_refH=0, f_startCX=0, f_peakSw=0, f_maxXF=0, f_cnt=0, f_latched=false;
        let s_minS=0, s_maxS=0, s_peakSp=0, s_maxKn=0, s_latched=false, s_frameCnt=0;

        function resetF() {{ f_refH=0; f_startCX=0; f_peakSw=0; f_maxXF=0; f_cnt=0; f_latched=false; }}
        function resetS() {{ s_minS=0; s_maxS=0; s_peakSp=0; s_maxKn=0; s_latched=false; s_frameCnt=0; }}

        const poseF = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        const poseS = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        [poseF, poseS].forEach(p => p.setOptions({{modelComplexity:0, smoothLandmarks:true}}));

        // 정면 엔진: 임팩트 감지 즉시 연산 루프 탈출
        poseF.onResults((r)=>{{
            if(!r.poseLandmarks || f_latched) return;
            const lm = r.poseLandmarks;
            const hL=lm[23], hR=lm[24], sL=lm[11], sR=lm[12];
            
            // [핵심] 임팩트 래치 강화: 손목이 배꼽 위치(골반 높이)에 도달하면 즉시 잠금
            if (lm[15].y > lm[23].y - 0.05) {{ f_latched = true; return; }}

            if(f_cnt < 20) {{
                f_refH = (f_refH * f_cnt + Math.abs(hL.x - hR.x)) / (f_cnt + 1);
                f_startCX = (hL.x + hR.x) / 2;
                f_cnt++;
            }} else {{
                let curSw = (((hL.x+hR.x)/2 - f_startCX) / f_refH) * 100;
                if(curSw > f_peakSw && curSw < 20) {{
                    f_peakSw = curSw;
                    document.getElementById('f_sw_l').innerText = f_peakSw.toFixed(1);
                }}
                let curXF = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                if(curXF > f_maxXF && curXF < 65) {{
                    f_maxXF = curXF;
                    document.getElementById('f_xf_l').innerText = (f_maxXF * 1.1).toFixed(1);
                }}
            }}
        }});

        // 측면 엔진: 데이터 고정 로직 강화
        poseS.onResults((r)=>{{
            if(!r.poseLandmarks || s_latched) return;
            const lm = r.poseLandmarks;
            const hC = (lm[23].y + lm[24].y) / 2;
            const sC = (lm[11].y + lm[12].y) / 2;
            const curSp = Math.abs(Math.atan2(hC - sC, (lm[23].x + lm[24].x)/2 - (lm[11].x + lm[12].x)/2) * 180/Math.PI);

            if (lm[15].y > lm[23].y - 0.05) {{ s_latched = true; return; }}

            if(s_frameCnt < 10) {{
                s_minS = curSp; s_maxS = curSp; s_frameCnt++;
            }} else {{
                if(curSp < s_minS) s_minS = curSp;
                if(curSp > s_maxS) s_maxS = curSp;
                let delta = s_maxS - s_minS;
                if(delta > s_peakSp && delta < 15) {{
                    s_peakSp = delta;
                    document.getElementById('s_sp_l').innerText = s_peakSp.toFixed(1);
                }}
            }}
            const curKn = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI);
            if(curKn > s_maxKn) {{
                s_maxKn = curKn;
                document.getElementById('s_kn_l').innerText = s_maxKn.toFixed(1);
            }}
        }});

        vf.onplay = () => {{ resetF(); loopF(); }};
        vs.onplay = () => {{ resetS(); loopS(); }};

        async function loopF() {{ while(!vf.paused && !f_latched){{ await poseF.send({{image:vf}}); await new Promise(r=>requestAnimationFrame(r)); }} }}
        async function loopS() {{ while(!vs.paused && !s_latched){{ await poseS.send({{image:vs}}); await new Promise(r=>requestAnimationFrame(r)); }} }}
        
        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
    </script>
    """

# [3] Streamlit 실행 로직
c1, c2 = st.columns(2)
with c1: f_f = st.file_uploader("Front Video", type=['mp4', 'mov'])
with c2: s_f = st.file_uploader("Side Video", type=['mp4', 'mov'])

if f_f and s_f:
    components.html(get_final_engine(base64.b64encode(f_f.read()).decode(), base64.b64encode(s_f.read()).decode()), height=500)
