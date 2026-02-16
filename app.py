import streamlit as st
import base64
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="GDR AI Pro v100")
st.title("⛳ GDR AI Pro: 엔진 분리 및 자세 기반 하드 래치 v100.0")

def get_decoupled_engine(f_v64, s_v64):
    return f"""
    <style>
        .v-box {{ background: #111; padding: 15px; border-radius: 12px; border: 1px solid #333; margin-bottom: 20px; }}
        video {{ width: 100%; border-radius: 10px; background: #000; }}
        .val-disp {{ margin-top:10px; color:#0f0; font-family:monospace; font-size:26px; font-weight:bold; background:rgba(0,0,0,0.5); padding:15px; border-radius:8px; border:1px solid #0f0; text-align:center; }}
        #log {{ font-size: 14px; color: #ff0; background: #222; padding: 10px; border-radius: 5px; margin-top: 10px; font-family: monospace; min-height: 40px; border: 1px dashed #555; }}
    </style>

    <div id="log">상태: 시스템 부팅 완료 (v100).</div>
    
    <div class="v-box">
        <h4 style="color:#0f0; margin:0;">FRONT VIEW</h4>
        <video id="vf" controls playsinline muted></video>
        <div class="val-disp">Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°</div>
    </div>

    <div class="v-box">
        <h4 style="color:#0f0; margin:0;">SIDE VIEW</h4>
        <video id="vs" controls playsinline muted></video>
        <div class="val-disp">Δ Spine: <span id="s_sp">0.0</span>° | Knee: <span id="s_kn">0.0</span>°</div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs'), log=document.getElementById('log');
        
        // [핵심] 정면/측면 데이터 공간 완전 격리
        let f_data = {{ pkSw:0, pkXF:0, c:0, lock:false, stCX:0, topReached:false }};
        let s_data = {{ pkSp:0, pkKn:0, c:0, lock:false, initS:0, topReached:false }};

        const pose = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:0, smoothLandmarks:true, minDetectionConfidence:0.4}});

        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hL=lm[24], hR=lm[23], sL=lm[12], sR=lm[11], wL=lm[16], wR=lm[15];
            
            // 1. 정면 분석 루프
            if (vf.playing && !f_data.lock) {{
                if (f_data.stCX === 0) f_data.stCX = (hL.x + hR.x) / 2;
                f_data.c++;

                // 자세 기반 래치 (손목이 어깨 위로 올라갔다가 다시 골반 아래로 내려오면 잠금)
                if (wL.y < sL.y) f_data.topReached = true; 
                if (f_data.topReached && wL.y > hL.y) {{
                    f_data.lock = true;
                    log.innerHTML = "<b style='color:#0f0;'>🎯 정면 임팩트 고정 완료</b>";
                }}

                if (!f_data.lock) {{
                    let sw = (((hL.x + hR.x)/2 - f_data.stCX) / 0.2) * 140;
                    if(sw > f_data.pkSw && sw < 22) f_data.pkSw = sw;
                    document.getElementById('f_sw').innerText = Math.abs(f_data.pkSw).toFixed(1);

                    let xf = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                    if(xf > f_data.pkXF && xf < 65) f_data.pkXF = xf;
                    document.getElementById('f_xf').innerText = (f_data.pkXF * 1.1).toFixed(1);
                }}
            }}

            // 2. 측면 분석 루프 (물리 격리)
            if (vs.playing && !s_data.lock) {{
                if(s_data.initS === 0) s_data.initS = Math.abs(Math.atan2(((lm[23].y+lm[24].y)/2)-((lm[11].y+lm[12].y)/2), ((lm[23].x+lm[24].x)/2)-((lm[11].x+lm[12].x)/2))*180/Math.PI);
                s_data.c++;

                // 측면 자세 기반 래치
                if (wR.y < lm[11].y) s_data.topReached = true;
                if (s_data.topReached && wR.y > lm[23].y) s_data.lock = true;

                if (!s_data.lock) {{
                    const hC = (lm[23].y + lm[24].y)/2, sC = (lm[11].y + lm[12].y)/2;
                    const sp = Math.abs(Math.atan2(hC-sC, (lm[23].x+lm[24].x)/2 - (lm[11].x+lm[12].x)/2) * 180/Math.PI);
                    let d = Math.abs(sp - s_data.initS);
                    if(d > s_data.pkSp && d < 18) s_data.pkSp = d;
                    document.getElementById('s_sp').innerText = s_data.pkSp.toFixed(1);
                    
                    let kn = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI);
                    if(kn > s_data.pkKn) s_data.pkKn = kn;
                    document.getElementById('s_kn').innerText = s_data.pkKn.toFixed(1);
                }}
            }}
        }});

        // 비디오 재생 상태 확장
        Object.defineProperty(HTMLVideoElement.prototype, 'playing', {{ get: function(){{ return !!(this.currentTime > 0 && !this.paused && !this.ended && this.readyState > 2); }} }});

        async function loop(v) {{
            while(v.playing) {{
                await pose.send({{image: v}});
                await new Promise(r => setTimeout(r, 55));
            }}
        }}

        vf.onplay = () => {{ 
            f_data = {{ pkSw:0, pkXF:0, c:0, lock:false, stCX:0, topReached:false }};
            document.getElementById('f_sw').innerText = "0.0";
            document.getElementById('f_xf').innerText = "0.0";
            loop(vf); 
        }};

        vs.onplay = () => {{ 
            s_data = {{ pkSp:0, pkKn:0, c:0, lock:false, initS:0, topReached:false }};
            document.getElementById('s_sp').innerText = "0.0";
            document.getElementById('s_kn').innerText = "0.0";
            loop(vs); 
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
    components.html(get_decoupled_engine(f_b, s_b), height=1400)
