import streamlit as st
import base64
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="GDR AI Pro v107")
st.title("⛳ GDR AI Pro: 0.2x 슬로우 분석 및 정밀 래치 v107.0")

def get_slow_engine(f_v64, s_v64):
    return f"""
    <style>
        .v-box {{ background: #111; padding: 15px; border-radius: 12px; border: 1px solid #333; margin-bottom: 20px; }}
        video {{ width: 100%; border-radius: 10px; background: #000; }}
        .val-disp {{ margin-top:10px; color:#0f0; font-family:monospace; font-size:26px; font-weight:bold; background:rgba(0,0,0,0.5); padding:15px; border-radius:8px; border:1px solid #0f0; text-align:center; }}
        #log {{ font-size: 14px; color: #ff0; background: #222; padding: 10px; border-radius: 5px; margin-top: 10px; }}
    </style>

    <div id="log">상태: 슬로우 분석 모드 준비 완료 (0.2x Speed)</div>
    
    <div class="v-box">
        <h4 style="color:#0f0; margin:0;">FRONT (0.2x Slow Analysis)</h4>
        <video id="vf" controls playsinline muted></video>
        <div class="val-disp">Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°</div>
    </div>

    <div class="v-box">
        <h4 style="color:#0f0; margin:0;">SIDE (0.2x Slow Analysis)</h4>
        <video id="vs" controls playsinline muted></video>
        <div class="val-disp">Δ Spine: <span id="s_sp">0.0</span>° | Knee: <span id="s_kn">0.0</span>°</div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs'), log=document.getElementById('log');
        let pose = null;
        let f_d = {{ pkSw:0, pkXF:0, c:0, lock:false, stCX:0, top:false }};
        let s_d = {{ pkSp:0, pkKn:0, c:0, lock:false, topS:0, top:false, initS:0 }};

        function initEngine() {{
            if(pose) pose.close();
            pose = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
            pose.setOptions({{modelComplexity:1, smoothLandmarks:true, minDetectionConfidence:0.45}});
            pose.onResults(onResults);
        }}

        function onResults(r) {{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hL=lm[24], hR=lm[23], sL=lm[12], sR=lm[11], wL=lm[16], wR=lm[15];

            // 1. 정면 분석 (슬로우 모드 최적화)
            if (!vf.paused && !f_d.lock) {{
                f_d.c++;
                let curCX = (hL.x + hR.x) / 2;
                if (f_d.c <= 5) {{
                    f_d.stCX = (f_d.stCX * (f_d.c-1) + curCX) / f_d.c;
                }} else {{
                    let sw = ((curCX - f_d.stCX) / 0.12) * 100;
                    if(sw > f_d.pkSw && sw < 22) f_d.pkSw = sw;
                    document.getElementById('f_sw').innerText = Math.max(0, f_d.pkSw).toFixed(1);

                    let xf = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                    if(xf > f_d.pkXF && xf < 68) f_d.pkXF = xf;
                    document.getElementById('f_xf').innerText = (f_d.pkXF * 1.1).toFixed(1);

                    // 하드 래치: 슬로우 모드에서는 더 정밀하게 손목 위치 감지
                    if (wL.y < sL.y) f_d.top = true;
                    if (f_d.top && wL.y > hL.y - 0.02) {{
                        f_d.lock = true;
                        log.innerText = "상태: 정면 임팩트 정밀 고정 완료";
                    }}
                }}
            }}

            // 2. 측면 분석 (배치기 및 임팩트 래치 동시 적용)
            if (!vs.paused && !s_d.lock) {{
                s_d.c++;
                const hCy = (lm[23].y + lm[24].y)/2, hCx = (lm[23].x + lm[24].x)/2;
                const sCy = (lm[11].y + lm[12].y)/2, sCx = (lm[11].x + lm[12].x)/2;
                const sp = Math.abs(Math.atan2(hCy - sCy, hCx - sCx) * 180/Math.PI);

                if (s_d.c <= 5) s_d.initS = sp;
                
                if (wR.y < lm[11].y) {{
                    s_d.top = true;
                    if (s_d.topS === 0) s_d.topS = sp;
                }}

                if (s_d.top) {{
                    let d_down = Math.abs(sp - s_d.topS);
                    if(d_down > s_d.pkSp) s_d.pkSp = d_down;
                    // 측면 임팩트 래치 강제 적용
                    if (wR.y > lm[23].y - 0.02) s_d.lock = true;
                }} else {{
                    let d_back = Math.abs(sp - s_d.initS);
                    if(d_back > s_d.pkSp) s_d.pkSp = d_back;
                }}
                document.getElementById('s_sp').innerText = s_d.pkSp.toFixed(1);
                
                let kn = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI);
                if(kn > s_d.pkKn) s_d.pkKn = kn;
                document.getElementById('s_kn').innerText = s_d.pkKn.toFixed(1);
            }}
        }}

        async function stream(v) {{
            v.playbackRate = 0.2; // [핵심] 재생 속도 0.2배속 고정
            while(!v.paused && !v.ended) {{
                await pose.send({{image: v}});
                await new Promise(r => setTimeout(r, 30));
            }}
        }}

        vf.onplay = () => {{ 
            initEngine();
            f_d = {{ pkSw:0, pkXF:0, c:0, lock:false, stCX:0, top:false }};
            stream(vf); 
        }};
        vs.onplay = () => {{ 
            if(!pose) initEngine();
            s_d = {{ pkSp:0, pkKn:0, c:0, lock:false, initS:0, topS:0, top:false }};
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
    components.html(get_slow_engine(f_b, s_b), height=1400)
