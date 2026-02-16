import streamlit as st
import base64
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="GDR AI Pro v99")
st.title("⛳ GDR AI Pro: 속도 기반 래칭 및 기준점 보정 v99.0")

def get_pro_engine(f_v64, s_v64):
    return f"""
    <style>
        .v-box {{ background: #111; padding: 15px; border-radius: 12px; border: 1px solid #333; margin-bottom: 20px; }}
        video {{ width: 100%; border-radius: 10px; background: #000; }}
        .val-disp {{ margin-top:10px; color:#0f0; font-family:monospace; font-size:26px; font-weight:bold; background:rgba(0,0,0,0.5); padding:15px; border-radius:8px; border:1px solid #0f0; text-align:center; }}
        #debug_log {{ font-size: 14px; color: #ff0; background: #222; padding: 10px; border-radius: 5px; margin-top: 10px; font-family: monospace; min-height: 40px; border: 1px dashed #555; }}
    </style>

    <div id="debug_log">상태: 시스템 부팅 완료.</div>
    
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
        
        let f_state = {{ pkSw:0, pkXF:0, c:0, lock:false, stCX:0, lastWY:0 }};
        let s_state = {{ pkSp:0, pkKn:0, c:0, lock:false, initS:0 }};

        const pose = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:0, smoothLandmarks:true, minDetectionConfidence:0.4}});

        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hL=lm[24], hR=lm[23], sL=lm[12], sR=lm[11], wL=lm[16];
            
            // 1. 정면 분석 (속도 기반 래치 적용)
            if (!f_state.lock) {{
                if (f_state.stCX === 0) f_state.stCX = (hL.x + hR.x) / 2;
                f_state.c++;

                let sw = (((hL.x + hR.x)/2 - f_state.stCX) / 0.2) * 140;
                if(sw > f_state.pkSw && sw < 20) f_state.pkSw = sw;
                document.getElementById('f_sw').innerText = Math.abs(f_state.pkSw).toFixed(1);

                let xf = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                if(xf > f_state.pkXF && xf < 65) f_state.pkXF = xf;
                document.getElementById('f_xf').innerText = (f_state.pkXF * 1.1).toFixed(1);

                // 속도 기반 임팩트 감지: 손목이 골반 아래로 내려오는 속도가 빠를 때만 래치
                let speed = Math.abs(wL.y - f_state.lastWY);
                if (f_state.c > 15 && wL.y > hL.y && speed > 0.01) {{
                    f_state.lock = true;
                    log.innerHTML = "<b style='color:#0f0;'>🎯 정면 임팩트 감지 성공</b>";
                }}
                f_state.lastWY = wL.y;
            }}

            // 2. 측면 분석 (기준점 보정 및 독립 래치)
            if (!s_state.lock) {{
                s_state.c++;
                const hC = (lm[23].y + lm[24].y)/2, sC = (lm[11].y + lm[12].y)/2;
                const sp = Math.abs(Math.atan2(hC-sC, (lm[23].x+lm[24].x)/2 - (lm[11].x+lm[12].x)/2) * 180/Math.PI);
                
                // 첫 10프레임 동안 기준점 안정화 (튀는 값 방지)
                if(s_state.c < 10) {{
                    s_state.initS = sp;
                }} else {{
                    let d = Math.abs(sp - s_state.initS);
                    if(d > s_state.pkSp && d < 15) s_state.pkSp = d;
                    document.getElementById('s_sp').innerText = s_state.pkSp.toFixed(1);
                    
                    let kn = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI);
                    if(kn > s_state.pkKn) s_state.pkKn = kn;
                    document.getElementById('s_kn').innerText = s_state.pkKn.toFixed(1);

                    // 측면 손목 위치 기반 래치
                    if (lm[16].y > lm[24].y) s_state.lock = true;
                }}
            }}
            log.innerText = `분석 가동 | F-Frame: ${{f_state.c}} | S-Frame: ${{s_state.c}}`;
        }});

        async function stream(v) {{
            while(!v.paused && !v.ended) {{
                await pose.send({{image: v}});
                await new Promise(r => setTimeout(r, 50));
            }}
        }}

        vf.onplay = () => {{ 
            f_state = {{ pkSw:0, pkXF:0, c:0, lock:false, stCX:0, lastWY:0 }};
            document.getElementById('f_sw').innerText = "0.0";
            document.getElementById('f_xf').innerText = "0.0";
            stream(vf); 
        }};

        vs.onplay = () => {{ 
            s_state = {{ pkSp:0, pkKn:0, c:0, lock:false, initS:0 }};
            document.getElementById('s_sp').innerText = "0.0";
            document.getElementById('s_kn').innerText = "0.0";
            stream(vs); 
        }};

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
    </script>
    """

f_f = st.file_uploader("Front Video", type=['mp4', 'mov'])
s_f = st.file_uploader("Side Video", type=['mp4', 'mov'])

if f_f and s_f:
    f_b = base64.b64encode(f_f.read()).decode()
    s_b = base64.b64encode(s_f.read()).decode()
    components.html(get_pro_engine(f_b, s_b), height=1400)
