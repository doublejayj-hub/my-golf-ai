import streamlit as st
import base64
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="GDR AI Pro v117")
st.title("⛳ GDR AI Pro: 재생 무결성 및 좌표 최종 교정 v117.0")

def get_final_stable_engine(f_v64, s_v64):
    return f"""
    <style>
        .v-box {{ position: relative; background: #000; border-radius: 12px; border: 1px solid #333; margin-bottom: 25px; overflow: hidden; }}
        video {{ width: 100%; display: block; z-index: 1; }}
        canvas {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 10; }}
        .val-disp {{ margin-top:10px; color:#0f0; font-family:monospace; font-size:26px; font-weight:bold; background:rgba(0,0,0,0.8); padding:15px; border-radius:8px; border:1px solid #0f0; text-align:center; }}
        #log {{ font-size: 14px; color: #ff0; background: #222; padding: 10px; text-align:center; }}
    </style>

    <div id="log">시스템 준비 완료. 재생 버튼을 눌러주세요.</div>
    
    <div class="v-box">
        <h4 style="color:#0f0; padding:10px;">FRONT: 골퍼 기준 왼발(타겟) 벽 가이드</h4>
        <video id="vf" controls playsinline muted></video>
        <canvas id="fc"></canvas>
        <div class="val-disp">Sway: <span id="f_sw">0.0</span>%</div>
    </div>

    <div class="v-box">
        <h4 style="color:#0f0; padding:10px;">SIDE: 엉덩이 최후방 Butt-Line</h4>
        <video id="vs" controls playsinline muted></video>
        <canvas id="sc"></canvas>
        <div class="val-disp">Δ Spine: <span id="s_sp">0.0</span>°</div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script>
        const vf=document.getElementById('vf'), vs=document.getElementById('vs');
        const fc=document.getElementById('fc'), sc=document.getElementById('sc');
        let pose = null, f_s = {{}}, s_s = {{}};

        // [핵심] 엔진 초기화 로직을 더 안전하게 분리
        async function loadPose() {{
            if (!pose) {{
                pose = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
                pose.setOptions({{modelComplexity:1, smoothLandmarks:true, minDetectionConfidence:0.5}});
                pose.onResults(onResults);
            }}
        }}

        function drawWall(ctx, canv, x, color) {{
            ctx.beginPath();
            ctx.setLineDash([15, 5]);
            ctx.moveTo(x * canv.width, 0);
            ctx.lineTo(x * canv.width, canv.height);
            ctx.strokeStyle = color;
            ctx.lineWidth = 6;
            ctx.stroke();
            ctx.setLineDash([]);
        }}

        function onResults(r) {{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            
            // 1. [정면] 골퍼 기준 왼발 (화면 우측 lm[28])
            if (!vf.paused) {{
                const fctx = fc.getContext('2d');
                fc.width = vf.offsetWidth; fc.height = vf.offsetHeight;
                fctx.clearRect(0, 0, fc.width, fc.height);
                
                if (f_s.c < 15) {{
                    f_s.wallX = ( (f_s.wallX || 0) * f_s.c + lm[28].x ) / (f_s.c + 1);
                    f_s.c++;
                }}
                if (f_s.wallX) drawWall(fctx, fc, f_s.wallX, '#00ff00');
                
                if(!f_s.stX) f_s.stX = (lm[23].x + lm[24].x) / 2;
                let sw = ((f_s.stX - (lm[23].x + lm[24].x)/2) / 0.1) * 100;
                document.getElementById('f_sw').innerText = Math.max(0, sw).toFixed(1);
            }}

            // 2. [측면] 엉덩이 최후방 (x값 최대 지점)
            if (!vs.paused) {{
                const sctx = sc.getContext('2d');
                sc.width = vs.offsetWidth; sc.height = vs.offsetHeight;
                sctx.clearRect(0, 0, sc.width, sc.height);
                
                let curButt = Math.max(lm[23].x, lm[24].x);
                if (s_s.c < 15) {{
                    s_s.buttX = ( (s_s.buttX || 0) * s_s.c + curButt ) / (s_s.c + 1);
                    s_s.c++;
                }}
                if (s_s.buttX) drawWall(sctx, sc, s_s.buttX, '#0000ff');
            }}
        }}

        async function startAnalysis(v) {{
            try {{
                await loadPose();
                v.playbackRate = 0.2; // 슬로우 모션 적용
                while(!v.paused && !v.ended) {{
                    await pose.send({{image: v}});
                    await new Promise(r => setTimeout(r, 50));
                }}
            }} catch(e) {{
                document.getElementById('log').innerText = "에러: " + e.message;
            }}
        }}

        vf.onplay = () => {{ f_s = {{c:0, stX:0}}; startAnalysis(vf); }};
        vs.onplay = () => {{ s_s = {{c:0}}; startAnalysis(vs); }};

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
    </script>
    """

f_file = st.file_uploader("Front Video (정면)", type=['mp4', 'mov'])
s_file = st.file_uploader("Side Video (측면)", type=['mp4', 'mov'])

if f_file and s_file:
    f_b = base64.b64encode(f_file.read()).decode()
    s_b = base64.b64encode(s_file.read()).decode()
    components.html(get_final_stable_engine(f_b, s_b), height=1600)
