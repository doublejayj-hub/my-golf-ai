import streamlit as st
import base64
import streamlit.components.v1 as components

# [1] 페이지 설정
st.set_page_config(layout="wide", page_title="GDR AI Pro v115")
st.title("⛳ GDR AI Pro: 에러 수정 및 물리 좌표 고정 v115.0")

# [2] 고정밀 분석 엔진 (TypeError 수정 및 물리적 좌표 매핑)
def get_final_stable_engine(f_v64, s_v64):
    return f"""
    <style>
        .v-box {{ position: relative; background: #000; border-radius: 12px; border: 1px solid #333; margin-bottom: 25px; overflow: hidden; }}
        video {{ width: 100%; display: block; z-index: 1; }}
        canvas {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 10; }}
        .val-disp {{ margin-top:10px; color:#0f0; font-family:monospace; font-size:26px; font-weight:bold; background:rgba(0,0,0,0.8); padding:15px; border-radius:8px; border:1px solid #0f0; text-align:center; }}
    </style>

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
        const fc=document.getElementById('fc'), fctx=fc.getContext('2d');
        const sc=document.getElementById('sc'), sctx=sc.getContext('2d');
        let pose = null, f_s = {{}}, s_s = {{}};

        function init() {{
            if(pose) pose.close();
            // 브라우저 캐시 영향 최소화를 위한 초기화
            pose = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
            pose.setOptions({{modelComplexity:1, smoothLandmarks:true, minDetectionConfidence:0.5}});
            pose.onResults(onResults);
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
            
            // 1. [정면] 골퍼 기준 왼발(타겟방향) 벽 가이드
            // 골퍼 정면 시 왼발은 화면상 '오른쪽 발'입니다 (x값이 큰 쪽)
            if (!vf.paused) {{
                fc.width = vf.offsetWidth; fc.height = vf.offsetHeight;
                fctx.clearRect(0, 0, fc.width, fc.height);
                
                // 화면상 우측 발(lm[28]) 좌표를 벽으로 고정 (15프레임 평균)
                if (f_s.c < 15) {{
                    f_s.wallX = ( (f_s.wallX || 0) * f_s.c + lm[28].x ) / (f_s.c + 1);
                    f_s.c++;
                }}
                if (f_s.wallX) drawWall(fctx, fc, f_s.wallX, '#00ff00');
                
                // Sway 연산 (기준점 대비 이동량)
                if(!f_s.stX) f_s.stX = (lm[23].x + lm[24].x) / 2;
                let sw = ((f_s.stX - (lm[23].x + lm[24].x)/2) / 0.1) * 100;
                document.getElementById('f_sw').innerText = Math.max(0, sw).toFixed(1);
            }}

            // 2. [측면] 엉덩이 최후방 Butt-Line
            // 측면에서 등 뒤 엉덩이는 화면상 '가장 오른쪽' 지점입니다
            if (!vs.paused) {{
                sc.width = vs.offsetWidth; sc.height = vs.offsetHeight;
                sctx.clearRect(0, 0, sc.width, sc.height);
                
                let currentButt = Math.max(lm[23].x, lm[24].x);
                if (s_s.c < 15) {{
                    s_s.buttX = ( (s_s.buttX || 0) * s_s.c + currentButt ) / (s_s.c + 1);
                    s_s.c++;
                }}
                if (s_s.buttX) drawWall(sctx, sc, s_s.buttX, '#0000ff');
            }}
        }}

        async function playSlow(v) {{
            v.playbackRate = 0.2;
            while(!v.paused && !v.ended) {{
                await pose.send({{image: v}});
                await new Promise(r => setTimeout(r, 45));
            }}
        }}

        vf.onplay = () => {{ init(); f_s = {{c:0, stX:0}}; playSlow(vf); }};
        vs.onplay = () => {{ init(); s_s = {{c:0}}; playSlow(vs); }};
    </script>
    """

# [3] 파일 업로드
f_file = st.file_uploader("Front Video (정면)", type=['mp4', 'mov'])
s_file = st.file_uploader("Side Video (측면)", type=['mp4', 'mov'])

if f_file and s_file:
    f_b = base64.b64encode(f_file.read()).decode()
    s_b = base64.b64encode(s_file.read()).decode()
    # TypeError 방지를 위해 인자에서 key 제거
    components.html(get_final_stable_engine(f_b, s_b), height=1600)
