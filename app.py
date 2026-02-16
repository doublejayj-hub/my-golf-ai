import streamlit as st
import base64
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="GDR AI Pro v97")
st.title("⛳ GDR AI Pro: 하드 리셋 및 메모리 퍼지 v97.0")

# [1] 고정밀 엔진 (세션 기반 완전 초기화 로직)
def get_hard_reset_engine(f_v64, s_v64):
    return f"""
    <style>
        .v-box {{ background: #111; padding: 15px; border-radius: 12px; border: 1px solid #333; margin-bottom: 20px; }}
        video {{ width: 100%; border-radius: 10px; background: #000; }}
        .val-disp {{ margin-top:10px; color:#0f0; font-family:monospace; font-size:26px; font-weight:bold; background:rgba(0,0,0,0.5); padding:15px; border-radius:8px; border:1px solid #0f0; text-align:center; }}
        #debug_log {{ font-size: 14px; color: #ff0; background: #222; padding: 10px; border-radius: 5px; margin-top: 10px; font-family: monospace; min-height: 40px; border: 1px dashed #555; }}
    </style>

    <div id="debug_log">상태: 엔진 부팅 완료. 재생 버튼을 눌러주세요.</div>
    
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
        
        // [핵심] 모든 연산 변수를 세션 객체로 관리
        let session = {{
            f: {{ pkSw:0, pkXF:0, c:0, lock:false, stCX:0, refH:0.2 }},
            s: {{ pkSp:0, pkKn:0, c:0, lock:false, initS:0 }}
        }};

        const pose = new Pose({{locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{p}}` }});
        pose.setOptions({{modelComplexity:0, smoothLandmarks:true, minDetectionConfidence:0.4}});

        pose.onResults((r)=>{{
            if(!r.poseLandmarks) return;
            const lm = r.poseLandmarks;
            const hL=lm[24], hR=lm[23], sL=lm[12], sR=lm[11], wL=lm[16];
            
            // 실시간 상태 업데이트
            log.innerText = `분석 중 | Frame: ${{++session.f.c}} | Wrist-Y: ${{wL.y.toFixed(3)}}`;

            // 자세 기반 지능형 래치 (세션 락 확인)
            if (!session.f.lock && session.f.c > 10) {{
                if (wL.y > hL.y - 0.03) {{ 
                    session.f.lock = true; session.s.lock = true;
                    log.innerHTML = "<b style='color:#0f0;'>🎯 임팩트 감지 - 최종 수치 고정</b>";
                    return;
                }}
            }}

            // 정면 분석
            if(!session.f.lock) {{
                if(session.f.stCX === 0) session.f.stCX = (hL.x + hR.x) / 2;
                
                let sw = (((hL.x + hR.x)/2 - session.f.stCX) / session.f.refH) * 140;
                if(sw > session.f.pkSw && sw < 20) session.f.pkSw = sw;
                document.getElementById('f_sw').innerText = Math.abs(session.f.pkSw).toFixed(1);

                let xf = Math.abs((Math.atan2(sR.y-sL.y, sR.x-sL.x) - Math.atan2(hR.y-hL.y, hR.x-hL.x)) * 180/Math.PI);
                if(xf > session.f.pkXF && xf < 65) session.f.pkXF = xf;
                document.getElementById('f_xf').innerText = (session.f.pkXF * 1.1).toFixed(1);
            }}

            // 측면 분석
            if(!session.s.lock) {{
                const hC = (lm[23].y + lm[24].y)/2, sC = (lm[11].y + lm[12].y)/2;
                const sp = Math.abs(Math.atan2(hC-sC, (lm[23].x+lm[24].x)/2 - (lm[11].x+lm[12].x)/2) * 180/Math.PI);
                if(session.s.initS === 0) session.s.initS = sp;
                let d = Math.abs(sp - session.s.initS);
                if(d > session.s.pkSp && d < 15) session.s.pkSp = d;
                document.getElementById('s_sp').innerText = session.s.pkSp.toFixed(1);
                
                let kn = Math.abs(Math.atan2(lm[26].y-lm[28].y, lm[26].x-lm[28].x)*180/Math.PI);
                if(kn > session.s.pkKn) session.s.pkKn = kn;
                document.getElementById('s_kn').innerText = session.s.pkKn.toFixed(1);
            }}
        }});

        async function run(v) {{
            while(!v.paused && !v.ended) {{
                await pose.send({{image: v}});
                await new Promise(r => setTimeout(r, 45));
            }}
        }}

        // [핵심] 재생 시 물리적 메모리 클리어 및 UI 리셋
        vf.onplay = () => {{ 
            session.f = {{ pkSw:0, pkXF:0, c:0, lock:false, stCX:0, refH:0.2 }};
            session.s = {{ pkSp:0, pkKn:0, c:0, lock:false, initS:0 }};
            document.querySelectorAll('span').forEach(s => s.innerText = "0.0");
            run(vf); 
        }};
        vs.onplay = () => {{ run(vs); }};

        vf.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{f_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
        vs.src = URL.createObjectURL(new Blob([Uint8Array.from(atob("{s_v64}"), c => c.charCodeAt(0))], {{type: 'video/mp4'}}));
    </script>
    """

f_f = st.file_uploader("Front Video", type=['mp4', 'mov'])
s_f = st.file_uploader("Side Video", type=['mp4', 'mov'])

if f_f and s_f:
    f_b = base64.b64encode(f_f.read()).decode()
    s_b = base64.b64encode(s_f.read()).decode()
    components.html(get_hard_reset_engine(f_b, s_b), height=1400)
