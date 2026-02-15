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

st.set_page_config(layout="wide", page_title="GDR AI Pro v62")
st.title("⛳ GDR AI Pro: 프레임 보간 및 임팩트 윈도우 v62.0")

# [2] 고정밀 엔진 (프레임 보간 및 임팩트 셧다운 로직)
def get_interpolated_engine(f_v64, s_v64):
    return f"""
    <div style="display: flex; gap: 15px; background: #000; padding: 20px; border-radius: 12px; border: 1px solid #333;">
        <div style="flex: 1; position: relative; text-align: center;">
            <h4 style="color: #0f0;">FRONT (Impact Window)</h4>
            <video id="vf" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div id="stats_f" style="margin-top:10px; background:rgba(0,255,0,0.1); color:#0f0; padding:12px; border-radius:8px; font-family:monospace; border:1px solid #0f0;">
                Sway: <span id="f_sw_v">0.0</span>% | X-Factor: <span id="f_xf_v">0.0</span>°
            </div>
        </div>
        <div style="flex: 1; position: relative; text-align: center;">
            <h4 style="color: #0f0;">SIDE (Impact Window)</h4>
            <video id="vs" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div id="stats_s" style="margin-top:10px; background:rgba(0,255,0,0.1); color:#0f0; padding:12px; border-radius:8px; font-family:monospace; border:1px solid #0f0;">
                Δ Spine: <span id="s_sp_v">0.0</span>° | Knee: <span id="s_kn_v">0.0</span>°
            </div>
        </div>
    </div>
    <div style="text-align: center; margin-top: 20px;">
        <button onclick="copyImpactData()" style="background:#0f0; color:#000; border:none; padding:15px 30px; border-radius:10px; cursor:pointer; font-weight:bold;">📋 임팩트 시점 데이터 복사</button>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs');
        let f_refH=0, f_startCX=0, f_peakSw=0, f_maxXF=0, f_cnt=0, isImpacted=false;
        let s_minS=180, s_maxS=0, s_peakSp=0, s_maxKn=0;

        function copyImpactData() {{
            const data = `[IMPACT_LOCKED_DATA]\\n` +
                         `Sway: ${{document.getElementById('f_sw_v').innerText}}%\\n` +
                         `X_Factor: ${{document.getElementById('f_xf_v').innerText}}deg\\n` +
                         `Spine_Delta: ${{document.getElementById('s_sp_v').innerText}}deg\\n` +
                         `Max_Knee: ${{document.getElementById('s_kn_v').innerText}}deg`;
            navigator.clipboard.writeText(data);
            alert("임팩트 이전 구간의 정규화 데이터가 복사되었습니다.");
        }}

        const poseF = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        const poseS = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        [poseF, poseS].forEach(p => p.setOptions({{modelComplexity:1, smoothLandmarks:true}}));

        poseF.onResults((r)=>{{
            if(!r.poseLandmarks || isImpacted) return;
            const lm = r.poseLandmarks;
            const hL=lm[23], hR=lm[24], sL=lm[11], sR=lm[12];
            
            // 임팩트 시점 감지: 어깨선이 타겟 방향으로 역전되기 시작하면 셧다운
            if (sR.x < hR.x - 0.05) {{ isImpacted = true; return; }}

            if(f_cnt < 20) {{
                f_refH = (f_refH * f_cnt + Math.abs(hL.x - hR.x)) / (f_cnt + 1);
                f_startCX = (hL.x + hR.x) / 2;
                f_cnt++;
            }} else {{
                const curSw = (( (hL.x + hR.x)/2 - f_startCX) / f_refH) * 100;
                if(curSw > f_peakSw && curSw < 20) f_peakSw = curSw;
                document.getElementById('f_sw_v').innerText = f_peakSw.toFixed(1);

                const curXF = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                if(curXF > f_maxXF && curXF < 65) f_maxXF = curXF;
                document.getElementById('f_xf_v').innerText = f_maxXF.toFixed(1);
            }}
        }});

        poseS.onResults((r)=>{{
            if(!r.poseLandmarks || isImpacted) return;
            const lm = r.poseLandmarks;
            const hC = {{x:(lm[23].x+lm[24].x)/2, y:(lm[23].y+lm[24].y)/2}};
            const sC = {{x:(lm[11].x+lm[12].x)/2, y:(lm[11].y+lm[12].y)/2}};
            const curSp = Math.abs(Math.atan2(hC.y-sC.y, hC.x-sC.x)*180/Math.PI);
            
            if(curSp > 40 && curSp < 140) {{
                if(curSp < s_minS) s_minS = curSp; if(curSp > s_maxS) s_maxS = curSp;
                const delta = s_maxS - s_minS;
                if(delta > s_peakSp) s_peakSp = delta;
                document.getElementById('s_sp_v').innerText = s_peakSp.toFixed(1);
            }}
            const curKn = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI);
            if(curKn > s_maxKn) s_maxKn = curKn;
            document.getElementById('s_kn_v').innerText = s_maxKn.toFixed(1);
        }});

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vf.onplay = async () => {{ isImpacted=false; while(!vf.paused){{ await poseF.send({{image:vf}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
        vs.onplay = async () => {{ while(!vs.paused){{ await poseS.send({{image:vs}}); await new Promise(r=>requestAnimationFrame(r)); }} }};
    </script>
    """

# [3] 파일 업로드 및 분석 리포트
c1, c2 = st.columns(2)
with c1: f_f = st.file_uploader("Front 영상", type=['mp4', 'mov'])
with c2: s_f = st.file_uploader("Side 영상", type=['mp4', 'mov'])

if f_f and s_f:
    components.html(get_interpolated_engine(base64.b64encode(f_f.read()).decode(), base64.b64encode(s_f.read()).decode()), height=600)

st.divider()
in_text = st.text_area("임팩트 이전 정점 데이터를 붙여넣으세요.")

if st.button("🚀 정밀 역학 분석 시작") and model:
    prompt = f"""
    당신은 운동역학 전문가입니다. 임팩트 시점에서 연산이 중단된 무결성 데이터를 분석하십시오.
    [데이터] {in_text}
    물리적 관점에서 축 유지와 비거리 효율을 진단하십시오. (개인적 언급 제외)
    """
    st.write(model.generate_content(prompt).text)
