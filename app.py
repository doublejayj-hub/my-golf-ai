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

st.set_page_config(layout="wide", page_title="GDR AI Pro v78")
st.title("⛳ GDR AI Pro: 하드 윈도우 및 정합성 패치 v78.0")

# [2] 고정밀 분석 엔진 (구간 강제 종료 로직)
def get_hard_window_engine(f_v64, s_v64):
    return f"""
    <div style="display: flex; gap: 10px; background: #000; padding: 15px; border-radius: 12px; border: 1px solid #333;">
        <div style="flex: 1; text-align: center;">
            <h4 style="color: #0f0; font-size: 14px;">FRONT (Impact Locked)</h4>
            <video id="vf" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div style="margin-top:10px; color:#0f0; font-family:monospace; background:rgba(0,255,0,0.1); padding:10px; border-radius:5px;">
                Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°
            </div>
        </div>
        <div style="flex: 1; text-align: center;">
            <h4 style="color: #0f0; font-size: 14px;">SIDE (Impact Locked)</h4>
            <video id="vs" controls playsinline style="width: 100%; border-radius: 8px;"></video>
            <div style="margin-top:10px; color:#0f0; font-family:monospace; background:rgba(0,255,0,0.1); padding:10px; border-radius:5px;">
                Δ Spine: <span id="s_sp">0.0</span>° | Knee: <span id="s_kn">0.0</span>°
            </div>
        </div>
    </div>
    <div id="status_log" style="margin-top:10px; padding:8px; background:#111; color:#0f0; font-size:12px;">상태: 대기 중...</div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs'), log=document.getElementById('status_log');
        let f_refH=0, f_startCX=0, f_pkSw=0, f_pkXF=0, f_c=0, f_lock=false;
        let s_minS=0, s_maxS=0, s_pkSp=0, s_pkKn=0, s_c=0, s_lock=false;

        const pose = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:0, smoothLandmarks:true}});

        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hL=lm[23], hR=lm[24], sL=lm[11], sR=lm[12];
            const wL=lm[15], wR=lm[16];

            // [핵심] 임팩트 래치: 손목이 골반 라인을 지나면 연산 완전 중단
            if (wL.y > hL.y - 0.05 || wR.y > hR.y - 0.05) {{ 
                f_lock = true; s_lock = true; 
                log.innerText = "상태: 임팩트 감지 - 데이터 고정됨";
                return; 
            }}

            // [정면] 정합성 필터 강화
            if(!f_lock) {{
                if(f_c < 15) {{ 
                    f_refH = Math.abs(hL.x - hR.x) || 0.1; 
                    f_startCX = (hL.x + hR.x)/2; f_c++; 
                }} else {{
                    // 백스윙 방향(x 증가)만 측정, 18% 이상 노이즈 컷
                    let sw = (((hL.x+hR.x)/2 - f_startCX) / f_refH) * 100;
                    if(sw > f_pkSw && sw < 18) f_pkSw = sw;
                    document.getElementById('f_sw').innerText = f_pkSw.toFixed(1);

                    let xf = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                    if(xf > f_pkXF && xf < 60) f_pkXF = xf; // 60도 이상 쓰레기값 방지
                    document.getElementById('f_xf').innerText = (f_pkXF * 1.1).toFixed(1);
                }}
            }}

            // [측면] 델타스파인 고정 강화
            if(!s_lock) {{
                const hC = (lm[23].y + lm[24].y)/2, sC = (lm[11].y + lm[12].y)/2;
                const sp = Math.abs(Math.atan2(hC - sC, (lm[23].x+lm[24].x)/2 - (lm[11].x+lm[12].x)/2) * 180/Math.PI);
                if(s_c < 10) {{ s_minS = sp; s_maxS = sp; s_c++; }} 
                else {{
                    if(sp < s_minS) s_minS = sp; if(sp > s_maxS) s_maxS = sp;
                    let d = s_maxS - s_minS;
                    // 임팩트 전 최대 변화량만 기록 (15도 상한)
                    if(d > s_pkSp && d < 15) s_pkSp = d;
                    document.getElementById('s_sp').innerText = s_pkSp.toFixed(1);
                }}
                let kn = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI);
                if(kn > s_pkKn) s_pkKn = kn;
                document.getElementById('s_kn').innerText = s_pkKn.toFixed(1);
            }}
        }});

        async function start(v) {{
            f_lock=false; s_lock=false;
            log.innerText = "상태: 분석 중...";
            while(!v.paused && !v.ended && !f_lock) {{
                await pose.send({{image: v}});
                await new Promise(r => setTimeout(r, 60));
            }}
        }}

        vf.onplay = () => {{ f_c=0; f_pkSw=0; f_pkXF=0; start(vf); }};
        vs.onplay = () => {{ s_c=0; s_pkSp=0; s_pkKn=0; start(vs); }};
        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
    </script>
    """

# [3] 파일 업로드
f_f = st.file_uploader("Front Video", type=['mp4', 'mov'])
s_f = st.file_uploader("Side Video", type=['mp4', 'mov'])

if f_f and s_f:
    f_b = base64.b64encode(f_f.read()).decode()
    s_b = base64.b64encode(s_f.read()).decode()
    components.html(get_hard_window_engine(f_b, s_b), height=550)

st.divider()
in_text = st.text_area("데이터를 붙여넣으세요.")
if st.button("🚀 종합 리포트 생성"):
    st.write(model.generate_content(f"전문가 분석: {in_text}").text)
