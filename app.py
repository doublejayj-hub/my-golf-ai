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

st.set_page_config(layout="wide", page_title="GDR AI Pro v69")
st.title("⛳ GDR AI Pro: 무중단 분석 및 하드 래치 시스템 v69.0")

# [2] 고안정성 분석 엔진 (이벤트 기반 프레임 처리)
def get_bulletproof_engine(f_v64, s_v64):
    return f"""
    <div style="display: flex; gap: 10px; background: #000; padding: 15px; border-radius: 12px; border: 1px solid #333;">
        <div style="flex: 1; text-align: center;">
            <h4 style="color: #0f0; font-size: 14px;">FRONT (Impact Lock)</h4>
            <video id="vf" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div id="stats_f" style="margin-top:8px; color:#0f0; font-family:monospace; font-size:15px; background:rgba(0,255,0,0.1); padding:10px; border-radius:5px;">
                Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°
            </div>
        </div>
        <div style="flex: 1; text-align: center;">
            <h4 style="color: #0f0; font-size: 14px;">SIDE (Impact Lock)</h4>
            <video id="vs" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div id="stats_s" style="margin-top:8px; color:#0f0; font-family:monospace; font-size:15px; background:rgba(0,255,0,0.1); padding:10px; border-radius:5px;">
                Δ Spine: <span id="s_sp">0.0</span>° | Knee: <span id="s_kn">0.0</span>°
            </div>
        </div>
    </div>
    <div style="text-align: center; margin-top: 15px;">
        <button onclick="copyData()" style="background:#0f0; color:#000; border:none; padding:12px 25px; border-radius:8px; cursor:pointer; font-weight:bold;">📋 역학 데이터 복사</button>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs');
        let f_refH=0, f_startCX=0, f_peakSw=0, f_maxXF=0, f_cnt=0, f_lock=false;
        let s_minS=0, s_maxS=0, s_peakSp=0, s_maxKn=0, s_lock=false, s_cal=false, s_cnt=0;

        function resetF() {{ f_refH=0; f_startCX=0; f_peakSw=0; f_maxXF=0; f_cnt=0; f_lock=false; }}
        function resetS() {{ s_minS=0; s_maxS=0; s_peakSp=0; s_maxKn=0; s_lock=false; s_cal=false; s_cnt=0; }}

        function copyData() {{
            const data = `[GDR_DATA]\\nF_Sway: ${{document.getElementById('f_sw').innerText}}%\\nF_XFactor: ${{document.getElementById('f_xf').innerText}}deg\\nS_SpineDelta: ${{document.getElementById('s_sp').innerText}}deg\\nS_Knee: ${{document.getElementById('s_kn').innerText}}deg`;
            navigator.clipboard.writeText(data); alert("데이터가 복사되었습니다.");
        }}

        const poseF = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        const poseS = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        [poseF, poseS].forEach(p => p.setOptions({{modelComplexity:0, smoothLandmarks:true}}));

        // 프레임 처리 최적화 (이벤트 대기 방식)
        poseF.onResults((r)=>{{
            if(!r.poseLandmarks || f_lock) return;
            const lm = r.poseLandmarks;
            if (lm[15].y > lm[23].y - 0.05) {{ f_lock = true; return; }} // 하드 래치

            const hL=lm[23], hR=lm[24], sL=lm[11], sR=lm[12];
            if(f_cnt < 15) {{
                f_refH = (f_refH * f_cnt + Math.abs(hL.x - hR.x)) / (f_cnt + 1);
                f_startCX = (hL.x + hR.x) / 2; f_cnt++;
            }} else if(f_refH > 0) {{
                let curSw = (((hL.x+hR.x)/2 - f_startCX) / f_refH) * 100;
                if(curSw > f_peakSw && curSw < 20) f_peakSw = curSw;
                document.getElementById('f_sw').innerText = f_peakSw.toFixed(1);

                let curXF = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                if(curXF > f_maxXF && curXF < 68) f_maxXF = curXF;
                document.getElementById('f_xf').innerText = (f_maxXF * 1.1).toFixed(1);
            }}
        }});

        poseS.onResults((r)=>{{
            if(!r.poseLandmarks || s_lock) return;
            const lm = r.poseLandmarks;
            if (lm[15].y > lm[23].y - 0.05) {{ s_lock = true; return; }} // 하드 래치

            const hC = (lm[23].y + lm[24].y) / 2;
            const sC = (lm[11].y + lm[12].y) / 2;
            const curSp = Math.abs(Math.atan2(hC - sC, (lm[23].x + lm[24].x)/2 - (lm[11].x + lm[12].x)/2) * 180/Math.PI);

            if(s_cnt < 10) {{ s_minS = curSp; s_maxS = curSp; s_cnt++; }} 
            else {{
                if(curSp < s_minS) s_minS = curSp;
                if(curSp > s_maxS) s_maxS = curSp;
                let delta = s_maxS - s_minS;
                if(delta > s_peakSp && delta < 15) s_peakSp = delta;
                document.getElementById('s_sp').innerText = s_peakSp.toFixed(1);
            }}
            const curKn = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI);
            if(curKn > s_maxKn) s_maxKn = curKn;
            document.getElementById('s_kn').innerText = s_maxKn.toFixed(1);
        }});

        // 재생 루프 안정화 (브라우저 부하 최적화)
        async function runEngine(v, p, lockObj) {{
            while(!v.paused && !v.ended) {{
                await p.send({{image: v}});
                await new Promise(requestAnimationFrame);
            }}
        }}

        vf.onplay = () => {{ resetF(); runEngine(vf, poseF); }};
        vs.onplay = () => {{ resetS(); runEngine(vs, poseS); }};

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
    </script>
    """

# [3] 파일 업로드
c1, c2 = st.columns(2)
with c1: f_f = st.file_uploader("Front Video", type=['mp4', 'mov'])
with c2: s_f = st.file_uploader("Side Video", type=['mp4', 'mov'])

if f_f and s_f:
    components.html(get_bulletproof_engine(base64.b64encode(f_f.read()).decode(), base64.b64encode(s_f.read()).decode()), height=550)

st.divider()
in_text = st.text_area("데이터를 붙여넣으세요.")
if st.button("🚀 종합 분석 리포트 생성") and model:
    st.write(model.generate_content(f"역학 전문가로서 분석하십시오: {in_text}").text)
