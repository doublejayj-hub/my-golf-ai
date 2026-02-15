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

st.set_page_config(layout="wide", page_title="GDR AI Pro v73")
st.title("⛳ GDR AI Pro: 사전 검증 무결성 패치 v73.0")

# [2] 고신뢰도 역학 엔진 (Frame-Sync 래치 시스템)
def get_validated_engine(f_v64, s_v64):
    return f"""
    <div style="display: flex; gap: 10px; background: #111; padding: 20px; border-radius: 12px; border: 1px solid #333;">
        <div style="flex: 1; text-align: center;">
            <h4 style="color: #0f0; font-size: 14px;">FRONT (Impact Locked)</h4>
            <video id="vf" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div id="stats_f" style="margin-top:10px; color:#0f0; font-family:monospace; font-size:16px; background:rgba(0,255,0,0.1); padding:10px; border-radius:5px;">
                Max Sway: <span id="f_sw">0.0</span>% | Max X-Factor: <span id="f_xf">0.0</span>°
            </div>
        </div>
        <div style="flex: 1; text-align: center;">
            <h4 style="color: #0f0; font-size: 14px;">SIDE (Impact Locked)</h4>
            <video id="vs" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div id="stats_s" style="margin-top:10px; color:#0f0; font-family:monospace; font-size:16px; background:rgba(0,255,0,0.1); padding:10px; border-radius:5px;">
                Δ Spine: <span id="s_sp">0.0</span>° | Max Knee: <span id="s_kn">0.0</span>°
            </div>
        </div>
    </div>
    <div style="text-align: center; margin-top: 15px;">
        <button onclick="copyData()" style="background:#0f0; color:#000; border:none; padding:12px 25px; border-radius:8px; cursor:pointer; font-weight:bold;">📋 역학 데이터 복사</button>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs');
        let f_refH=0, f_startCX=0, f_pkSw=0, f_pkXF=0, f_c=0, f_lock=false;
        let s_minS=0, s_maxS=0, s_pkSp=0, s_pkKn=0, s_c=0, s_lock=false;

        // [사전검증 1] 재생 시 완전 초기화 보장
        function forceClear() {{
            f_refH=0; f_startCX=0; f_pkSw=0; f_pkXF=0; f_c=0; f_lock=false;
            s_minS=0; s_maxS=0; s_pkSp=0; s_pkKn=0; s_c=0; s_lock=false;
            document.getElementById('f_sw').innerText = "0.0";
            document.getElementById('f_xf').innerText = "0.0";
            document.getElementById('s_sp').innerText = "0.0";
            document.getElementById('s_kn').innerText = "0.0";
        }}

        function copyData() {{
            const res = `[GDR_FINAL]\\nF_Sway: ${{document.getElementById('f_sw').innerText}}%\\nF_XF: ${{document.getElementById('f_xf').innerText}}deg\\nS_Spine: ${{document.getElementById('s_sp').innerText}}deg\\nS_Knee: ${{document.getElementById('s_kn').innerText}}deg`;
            navigator.clipboard.writeText(res); alert("데이터 복사 완료");
        }}

        const poseF = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        const poseS = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        [poseF, poseS].forEach(p => p.setOptions({{modelComplexity:0, smoothLandmarks:true}}));

        // [사전검증 2] 비동기 Deadlock 방지 프레임 루프
        async function processFrame(v, p, type) {{
            if (v.paused || v.ended) return;
            await p.send({{image: v}});
            v.requestVideoFrameCallback(() => processFrame(v, p, type));
        }}

        poseF.onResults((r)=>{{
            if(!r.poseLandmarks || f_lock) return;
            const lm = r.poseLandmarks;
            // 임팩트 시점 래치: 손목 가동 범위 기반
            if (lm[15].y > lm[23].y - 0.05) {{ f_lock = true; return; }}

            const hL=lm[23], hR=lm[24], sL=lm[11], sR=lm[12];
            if(f_c < 15) {{ f_refH = Math.abs(hL.x - hR.x); f_startCX = (hL.x + hR.x)/2; f_c++; }} 
            else {{
                let sw = (((hL.x+hR.x)/2 - f_startCX) / f_refH) * 100;
                if(sw > f_pkSw && sw < 18) f_pkSw = sw; // Sway 정합성 캡핑
                document.getElementById('f_sw').innerText = f_pkSw.toFixed(1);

                let xf = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                if(xf > f_pkXF && xf < 65) f_pkXF = xf;
                document.getElementById('f_xf').innerText = (f_pkXF * 1.1).toFixed(1);
            }}
        }});

        poseS.onResults((r)=>{{
            if(!r.poseLandmarks || s_lock) return;
            const lm = r.poseLandmarks;
            const hC = (lm[23].y + lm[24].y)/2, sC = (lm[11].y + lm[12].y)/2;
            if (lm[15].y > lm[23].y - 0.05) {{ s_lock = true; return; }}

            const sp = Math.abs(Math.atan2(hC - sC, (lm[23].x+lm[24].x)/2 - (lm[11].x+lm[12].x)/2) * 180/Math.PI);
            if(s_c < 10) {{ s_minS = sp; s_maxS = sp; s_c++; }} 
            else {{
                if(sp < s_minS) s_minS = sp; if(sp > s_maxS) s_maxS = sp;
                let d = s_maxS - s_minS;
                if(d > s_pkSp && d < 12) s_pkSp = d; // Spine 정합성 캡핑
                document.getElementById('s_sp').innerText = s_pkSp.toFixed(1);
            }}
            let kn = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI);
            if(kn > s_pkKn) s_pkKn = kn;
            document.getElementById('s_kn').innerText = s_pkKn.toFixed(1);
        }});

        vf.onplay = () => {{ forceClear(); processFrame(vf, poseF, 'F'); }};
        vs.onplay = () => {{ processFrame(vs, poseS, 'S'); }};

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
    </script>
    """

# [3] 파일 업로드
c1, c2 = st.columns(2)
with c1: f_f = st.file_uploader("Front Video", type=['mp4', 'mov'])
with c2: s_f = st.file_uploader("Side Video", type=['mp4', 'mov'])

if f_f and s_f:
    f_b = base64.b64encode(f_f.read()).decode()
    s_b = base64.b64encode(s_f.read()).decode()
    components.html(get_validated_engine(f_b, s_b), height=550)

st.divider()
in_text = st.text_area("데이터를 붙여넣으세요.")
if st.button("🚀 정밀 분석 리포트 생성") and model:
    st.write(model.generate_content(f"운동역학 전문가로서 기술적 분석 수행: {in_text}").text)
