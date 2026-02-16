import streamlit as st
import base64
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="GDR AI Pro v96")
st.title("⛳ GDR AI Pro: 관절 인식 무결성 패치 v96.0")

# [1] UI 가시성 확보를 위한 Streamlit 네이티브 상태창
status_placeholder = st.empty()
status_placeholder.info("준비 완료. 아래 플레이어에서 영상을 재생하세요.")

# [2] 고정밀 엔진 (관절 좌표 다이렉트 가시화)
def get_visibility_engine(f_v64, s_v64):
    return f"""
    <style>
        .v-box {{ background: #111; padding: 15px; border-radius: 12px; border: 1px solid #333; margin-bottom: 20px; }}
        video {{ width: 100%; border-radius: 10px; background: #000; }}
        .val-disp {{ margin-top:10px; color:#0f0; font-family:monospace; font-size:24px; font-weight:bold; background:rgba(0,0,0,0.5); padding:15px; border-radius:8px; border:1px solid #0f0; text-align:center; }}
        #debug_log {{ font-size: 14px; color: #ff0; background: #222; padding: 10px; border-radius: 5px; margin-top: 10px; font-family: monospace; min-height: 40px; border: 1px dashed #555; }}
    </style>

    <div id="debug_log">엔진 상태: 초기화 중...</div>
    
    <div class="v-box">
        <video id="vf" controls playsinline muted></video>
        <div class="val-disp">Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°</div>
    </div>

    <div class="v-box">
        <video id="vs" controls playsinline muted></video>
        <div class="val-disp">Δ Spine: <span id="s_sp">0.0</span>° | Knee: <span id="s_kn">0.0</span>°</div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs'), log=document.getElementById('debug_log');
        let f_pkSw=0, f_pkXF=0, f_c=0, f_lock=false, s_pkSp=0, s_pkKn=0, s_c=0, s_lock=false;
        let f_stCX=0, s_initS=0;

        const pose = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:0, smoothLandmarks:true, minDetectionConfidence:0.4}});

        pose.onResults((r)=>{{
            if(!r.poseLandmarks) {{
                log.innerText = "⚠️ 인물을 찾는 중... (관절 인식 실패)";
                return;
            }}
            
            const lm = r.poseLandmarks;
            const hL=lm[24], hR=lm[23], sL=lm[12], sR=lm[11], wL=lm[16], wR=lm[15];
            
            // 디버그 정보 출력: 실시간 좌표 수신 확인
            log.innerText = `✅ 분석 중 | Frame: ${{++f_c}} | Hip-Y: ${{hL.y.toFixed(3)}} | Wrist-Y: ${{wL.y.toFixed(3)}}`;

            // 자세 기반 지능형 래치
            if (!f_lock && f_c > 10) {{
                // 손목이 골반 라인 아래로 내려오면 임팩트로 판정
                if (wL.y > hL.y - 0.02) {{ 
                    f_lock = true; s_lock = true;
                    log.innerHTML = "<b style='color:#0f0;'>🎯 임팩트 자세 인식 성공 - 데이터 고정됨</b>";
                    return;
                }}
            }}

            if(!f_lock) {{
                if(f_stCX === 0) f_stCX = (hL.x + hR.x) / 2;
                let sw = (((hL.x + hR.x)/2 - f_stCX) / 0.2) * 130;
                if(sw > f_pkSw && sw < 18) f_pkSw = sw;
                document.getElementById('f_sw').innerText = f_pkSw.toFixed(1);

                let xf = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                if(xf > f_pkXF && xf < 65) f_pkXF = xf;
                document.getElementById('f_xf').innerText = (f_pkXF * 1.1).toFixed(1);
            }}

            if(!s_lock) {{
                const hC = (lm[23].y + lm[24].y)/2, sC = (lm[11].y + lm[12].y)/2;
                const sp = Math.abs(Math.atan2(hC-sC, (lm[23].x+lm[24].x)/2 - (lm[11].x+lm[12].x)/2) * 180/Math.PI);
                if(s_initS === 0) s_initS = sp;
                let d = Math.abs(sp - s_initS);
                if(d > s_pkSp && d < 15) s_pkSp = d;
                document.getElementById('s_sp').innerText = s_pkSp.toFixed(1);
                let kn = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI);
                if(kn > s_pkKn) s_pkKn = kn;
                document.getElementById('s_kn').innerText = s_pkKn.toFixed(1);
            }}
        }});

        async function stream(v) {{
            while(!v.paused && !v.ended) {{
                await pose.send({{image: v}});
                await new Promise(r => setTimeout(r, 40));
            }}
        }}

        vf.onplay = () => {{ f_pkSw=0; f_pkXF=0; f_c=0; f_lock=false; f_stCX=0; stream(vf); }};
        vs.onplay = () => {{ s_pkSp=0; s_pkKn=0; s_lock=false; s_initS=0; stream(vs); }};

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
    </script>
    """

f_f = st.file_uploader("Front Video", type=['mp4', 'mov'])
s_f = st.file_uploader("Side Video", type=['mp4', 'mov'])

if f_f and s_f:
    f_b = base64.b64encode(f_f.read()).decode()
    s_b = base64.b64encode(s_f.read()).decode()
    components.html(get_visibility_engine(f_b, s_b), height=1400)
