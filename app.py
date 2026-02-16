import streamlit as st
import base64
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="GDR AI Pro v105")
st.title("⛳ GDR AI Pro: 상태 머신 초기화 및 물리 래치 v105.0")

def get_final_engine(f_v64, s_v64):
    return f"""
    <style>
        .v-box {{ background: #111; padding: 15px; border-radius: 12px; border: 1px solid #333; margin-bottom: 20px; }}
        video {{ width: 100%; border-radius: 10px; background: #000; }}
        .val-disp {{ margin-top:10px; color:#0f0; font-family:monospace; font-size:26px; font-weight:bold; background:rgba(0,0,0,0.5); padding:15px; border-radius:8px; border:1px solid #0f0; text-align:center; }}
        #log {{ font-size: 14px; color: #ff0; background: #222; padding: 10px; border-radius: 5px; margin-top: 10px; min-height: 20px; }}
    </style>

    <div id="log">상태: 분석 대기 중...</div>
    
    <div class="v-box">
        <h4 style="color:#0f0; margin:0;">FRONT VIEW (Sway/X-Factor)</h4>
        <video id="vf" controls playsinline muted></video>
        <div class="val-disp">Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°</div>
    </div>

    <div class="v-box">
        <h4 style="color:#0f0; margin:0;">SIDE VIEW (Δ Spine/Knee)</h4>
        <video id="vs" controls playsinline muted></video>
        <div class="val-disp">Δ Spine: <span id="s_sp">0.0</span>° | Knee: <span id="s_kn">0.0</span>°</div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs'), log=document.getElementById('log');
        let pose = null;
        // 상태 객체 완전 분리 및 초기화 로직 강화
        let f_d = {{ pkSw:0, pkXF:0, c:0, lock:false, stCX:0, top:false }};
        let s_d = {{ pkSp:0, pkKn:0, c:0, lock:false, initS:0, top:false }};

        function initEngine() {{
            if(pose) {{ pose.close(); }}
            pose = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
            pose.setOptions({{modelComplexity:0, smoothLandmarks:true, minDetectionConfidence:0.45}});
            pose.onResults(onResults);
        }}

        function onResults(r) {{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hL=lm[24], hR=lm[23], sL=lm[12], sR=lm[11], wL=lm[16], wR=lm[15];

            // 1. 정면 분석 (재생 중이고 락이 걸리지 않았을 때만 연산)
            if (!vf.paused && !f_d.lock) {{
                f_d.c++;
                // [개선] 1~2프레임에서 강제 영점 조절 (백스윙 즉시 반영)
                if (f_d.c <= 2) f_d.stCX = (hL.x + hR.x) / 2;

                if (f_d.stCX > 0) {{
                    let curCX = (hL.x + hR.x) / 2;
                    let sw = ((curCX - f_d.stCX) / 0.12) * 100;
                    if(sw > f_d.pkSw && sw < 22) f_d.pkSw = sw;
                    document.getElementById('f_sw').innerText = Math.abs(f_d.pkSw).toFixed(1);

                    let xf = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                    if(xf > f_d.pkXF && xf < 70) f_d.pkXF = xf;
                    document.getElementById('f_xf').innerText = (f_d.pkXF * 1.1).toFixed(1);
                }}

                // [강력한 하드 래치] 백스윙 탑 도달 후, 손목이 어깨 아래(임팩트 구간)로 오면 영구 잠금
                if (wL.y < sL.y) f_d.top = true;
                if (f_d.top && wL.y > (hL.y - 0.1)) {{
                    f_d.lock = true;
                    log.innerText = "상태: 정면 분석 완료 (임팩트 래치 고정)";
                }}
            }}

            // 2. 측면 분석 (독립 상태 머신)
            if (!vs.paused && !s_d.lock) {{
                s_d.c++;
                const hCy = (lm[23].y + lm[24].y)/2, hCx = (lm[23].x + lm[24].x)/2;
                const sCy = (lm[11].y + lm[12].y)/2, sCx = (lm[11].x + lm[12].x)/2;
                const sp = Math.abs(Math.atan2(hCy - sCy, hCx - sCx) * 180/Math.PI);
                
                if(s_d.c <= 2) s_d.initS = sp;
                else {{
                    let d = Math.abs(sp - s_d.initS);
                    if(d > s_d.pkSp && d < 18) s_d.pkSp = d;
                    document.getElementById('s_sp').innerText = s_d.pkSp.toFixed(1);

                    let kn = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI);
                    if(kn > s_d.pkKn) s_d.pkKn = kn;
                    document.getElementById('s_kn').innerText = s_d.pkKn.toFixed(1);

                    if (wR.y < sR.y) s_d.top = true;
                    if (s_d.top && wR.y > (hR.y - 0.1)) s_d.lock = true;
                }}
            }}
        }}

        async function stream(v) {{
            while(!v.paused && !v.ended) {{
                await pose.send({{image: v}});
                await new Promise(r => setTimeout(r, 45));
            }}
        }}

        // [핵심] 재생 버튼 클릭 시 모든 데이터와 엔진을 물리적으로 리셋
        vf.onplay = () => {{ 
            initEngine();
            f_d = {{ pkSw:0, pkXF:0, c:0, lock:false, stCX:0, top:false }};
            document.getElementById('f_sw').innerText = "0.0";
            document.getElementById('f_xf').innerText = "0.0";
            log.innerText = "상태: 정면 분석 시작";
            stream(vf); 
        }};

        vs.onplay = () => {{ 
            initEngine();
            s_d = {{ pkSp:0, pkKn:0, c:0, lock:false, initS:0, top:false }};
            document.getElementById('s_sp').innerText = "0.0";
            document.getElementById('s_kn').innerText = "0.0";
            log.innerText = "상태: 측면 분석 시작";
            stream(vs); 
        }};

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
    </script>
    """

f_file = st.file_uploader("Front Video (정면)", type=['mp4', 'mov'])
s_file = st.file_uploader("Side Video (측면)", type=['mp4', 'mov'])

if f_file and s_file:
    f_b64 = base64.b64encode(f_file.read()).decode()
    s_b64 = base64.b64encode(s_file.read()).decode()
    components.html(get_final_engine(f_b64, s_b64), height=1400)
