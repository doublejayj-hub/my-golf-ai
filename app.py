import streamlit as st
import base64
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="GDR AI Pro v109")
st.title("⛳ GDR AI Pro: 재생 무결성 및 레이어 최적화 v109.0")

def get_stable_overlay_engine(f_v64, s_v64):
    return f"""
    <style>
        .v-box {{ position: relative; background: #000; padding: 0; border-radius: 12px; border: 1px solid #333; margin-bottom: 25px; overflow: hidden; }}
        video {{ width: 100%; display: block; z-index: 1; }}
        /* 캔버스가 비디오 클릭을 방해하지 않도록 설정 */
        canvas {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 2; }}
        .val-disp {{ margin-top:10px; color:#0f0; font-family:monospace; font-size:26px; font-weight:bold; background:rgba(0,0,0,0.8); padding:15px; border-radius:8px; border:1px solid #0f0; text-align:center; }}
        #log {{ font-size: 14px; color: #ff0; background: #222; padding: 10px; text-align:center; margin-bottom: 10px; border-radius: 5px; }}
    </style>

    <div id="log">시스템 준비 완료. 영상을 재생하세요.</div>
    
    <div class="v-box">
        <video id="vf" controls playsinline muted></video>
        <div class="val-disp">Sway: <span id="f_sw">0.0</span>% | X-Factor: <span id="f_xf">0.0</span>°</div>
    </div>

    <div class="v-box">
        <video id="vs" controls playsinline muted></video>
        <canvas id="side_canvas"></canvas>
        <div class="val-disp">Δ Spine: <span id="s_sp">0.0</span>° | Knee: <span id="s_kn">0.0</span>°</div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs');
        const sc=document.getElementById('side_canvas'), ctx=sc.getContext('2d');
        let pose = null, f_d = {{}}, s_d = {{}};

        // [무결성] 엔진 초기화 안정성 확보
        function initEngine() {{
            if(pose) {{ pose.close(); }}
            pose = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
            pose.setOptions({{modelComplexity:1, smoothLandmarks:true, minDetectionConfidence:0.5}});
            pose.onResults(onResults);
        }}

        function drawLine(p1, p2, color, width=2) {{
            ctx.beginPath();
            ctx.moveTo(p1.x * sc.width, p1.y * sc.height);
            ctx.lineTo(p2.x * sc.width, p2.y * sc.height);
            ctx.strokeStyle = color;
            ctx.lineWidth = width;
            ctx.stroke();
        }}

        function onResults(r) {{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hL=lm[24], hR=lm[23], sL=lm[12], sR=lm[11], wL=lm[16], wR=lm[15];

            // 1. 정면 분석 (방향 교정 로직 유지)
            if (!vf.paused && !f_d.lock) {{
                f_d.c++;
                let curCX = (hL.x + hR.x) / 2;
                if (f_d.c <= 5) f_d.stCX = curCX;
                else {{
                    let sw = ((f_d.stCX - curCX) / 0.1) * 100; // 백스윙 방향 양수화
                    if(sw > f_d.pkSw && sw < 25) f_d.pkSw = sw;
                    document.getElementById('f_sw').innerText = Math.max(0, f_d.pkSw).toFixed(1);

                    let xf = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                    if(xf > f_d.pkXF && xf < 68) f_d.pkXF = xf;
                    document.getElementById('f_xf').innerText = (f_d.pkXF * 1.1).toFixed(1);

                    if (wL.y < sL.y) f_d.top = true;
                    if (f_d.top && wL.y > hL.y - 0.05) f_d.lock = true;
                }}
            }}

            // 2. 측면 분석 (3단 가이드 오버레이 무결성)
            if (!vs.paused && !s_d.lock) {{
                s_d.c++;
                sc.width = vs.offsetWidth; sc.height = vs.offsetHeight;
                const hC = {{x:(lm[23].x+lm[24].x)/2, y:(lm[23].y+lm[24].y)/2}};
                const sC = {{x:(lm[11].x+lm[12].x)/2, y:(lm[11].y+lm[12].y)/2}};
                const curSp = Math.abs(Math.atan2(hC.y - sC.y, hC.x - sC.x) * 180/Math.PI);

                ctx.clearRect(0, 0, sc.width, sc.height);
                
                // 가이드라인 렌더링
                if (s_d.c === 10) s_d.addr = {{s:sC, h:hC, ang:curSp}};
                if (s_d.addr) drawLine(s_d.addr.s, s_d.addr.h, '#00f', 2); // 어드레스(청색)

                if (wR.y < lm[11].y) {{
                    s_d.topP = true;
                    if (!s_d.topL || curSp > s_d.topL.ang) s_d.topL = {{s:sC, h:hC, ang:curSp}};
                }}
                if (s_d.topL) drawLine(s_d.topL.s, s_d.topL.h, '#f00', 2); // 탑(적색)

                if (s_d.topP && wR.y > lm[23].y - 0.02) {{
                    s_d.lock = true;
                    s_d.impL = {{s:sC, h:hC}}; // 임팩트(녹색)
                }}

                drawLine(sC, hC, '#0f0', 3); // 실시간 척추선
                if(s_d.impL) drawLine(s_d.impL.s, s_d.impL.h, '#0f0', 4);
                
                let d = s_d.addr ? Math.abs(curSp - s_d.addr.ang) : 0;
                if(s_d.topP) {{
                    let d_down = Math.abs(curSp - s_d.topL.ang);
                    if(d_down > s_d.pkSp) s_d.pkSp = d_down;
                }} else if(d > s_d.pkSp) s_d.pkSp = d;

                document.getElementById('s_sp').innerText = s_d.pkSp.toFixed(1);
                let kn = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI);
                if(kn > s_d.pkKn) s_d.pkKn = kn;
                document.getElementById('s_kn').innerText = s_d.pkKn.toFixed(1);
            }}
        }}

        async function loop(v) {{
            v.playbackRate = 0.2;
            while(!v.paused && !v.ended) {{
                await pose.send({{image: v}});
                await new Promise(r => setTimeout(r, 40));
            }}
        }}

        // [리셋] 비디오 컨트롤 방해 금지 설정
        vf.onplay = () => {{ 
            initEngine(); f_d = {{ pkSw:0, pkXF:0, c:0, lock:false, stCX:0, top:false }};
            loop(vf); 
        }};
        vs.onplay = () => {{ 
            initEngine(); s_d = {{ pkSp:0, pkKn:0, c:0, lock:false, addr:null, topL:null, impL:null, topP:false }};
            loop(vs); 
        }};

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
    </script>
    """

f_file = st.file_uploader("Front Video (정면)", type=['mp4', 'mov'])
s_file = st.file_uploader("Side Video (측면)", type=['mp4', 'mov'])

if f_file and s_file:
    f_b = base64.b64encode(f_file.read()).decode()
    s_b = base64.b64encode(s_file.read()).decode()
    components.html(get_stable_overlay_engine(f_b, s_b), height=1500)
