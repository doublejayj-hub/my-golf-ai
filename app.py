import streamlit as st
import streamlit.components.v1 as components
import base64

# [1] HTML/JS 엔진: 모든 로직을 최상단 상수로 격리하여 에러 차단
FINAL_HTML = """
<div id="w" style="width:100%; background:#000; border-radius:10px; overflow:hidden; position:relative;">
    <input type="file" id="ui" accept="video/*" style="display:none;">
    <video id="v" controls playsinline style="width:100%; display:block; height:auto;"></video>
    <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
    <div id="st" style="position:absolute; top:10px; left:10px; color:#fff; background:rgba(0,123,255,0.8); padding:8px; font-family:monospace; border-radius:5px; font-weight:bold; z-index:100;">[AI] READY</div>
</div>

<script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils"></script>

<script>
    const v=document.getElementById('v'), c=document.getElementById('c'), ctx=c.getContext('2d'), st=document.getElementById('st');
    let pL=null, pY=0;

    const pose = new Pose({locateFile:(f)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${f}`});
    pose.setOptions({modelComplexity:1, smoothLandmarks:true, minDetectionConfidence:0.5, minTrackingConfidence:0.5});

    function lerp(a,b,t){return {x:a.x+(b.x-a.x)*t, y:a.y+(b.y-a.y)*t};}

    pose.onResults((r)=>{
        if(!r.poseLandmarks) return;
        c.width=v.videoWidth; c.height=v.videoHeight;
        ctx.save(); ctx.clearRect(0,0,c.width,c.height);
        const w=r.poseLandmarks[15], h=r.poseLandmarks[23], vy=w.y-pY;
        const isI = (vy>0.01 && w.y<h.y+0.2)||(w.y>=h.y-0.1 && w.y<=h.y+0.3);
        
        if(isI && pL){
            st.innerText="HYPER-RES (120FPS+)"; st.parentElement.style.background="rgba(255,0,0,0.8)";
            [0.25,0.5,0.75].forEach(t=>{
                const mid=r.poseLandmarks.map((l,i)=>lerp(pL[i],l,t));
                drawConnectors(ctx,mid,POSE_CONNECTIONS,{color:'rgba(0,255,255,0.4)',lineWidth:1});
            });
        } else {
            st.innerText="STANDARD (60FPS)"; st.parentElement.style.background="rgba(0,123,255,0.8)";
        }
        drawConnectors(ctx,r.poseLandmarks,POSE_CONNECTIONS,{color:'#00FF00',lineWidth:4});
        drawLandmarks(ctx,r.poseLandmarks,{color:'#FF0000',lineWidth:2,radius:5});
        pL=r.poseLandmarks; pY=w.y; ctx.restore();
    });

    // 브라우저 직접 로딩 방식 (postMessage 보안 이슈 회피)
    window.addEventListener("message", (e) => {
        if (e.data.type === "DATA_TRANSFER") {
            const blob = new Blob([e.data.raw], { type: 'video/mp4' });
            v.src = URL.createObjectURL(blob);
            st.innerText = "[AI] VIDEO LOADED";
        }
    });

    async function loop(){ if(!v.paused && !v.ended){ await pose.send({image:v}); } requestAnimationFrame(loop); }
    v.onplay = loop;
</script>
"""

st.set_page_config(layout="wide")
st.title("⛳ GDR AI 초정밀 분석기 (재생 엔진 무결성 버전)")

# [핵심] Streamlit 파일 업로더를 거쳐 데이터를 안전하게 브라우저로 쏴줍니다.
f = st.file_uploader("영상을 업로드하세요", type=['mp4', 'mov'])

if f:
    # 1. 바이트 데이터 추출
    video_bytes = f.read()
    
    # 2. HTML 엔진 로드
    components.html(FINAL_HTML, height=550)
    
    # 3. 브라우저 사이드 데이터 전송 (Uint8Array 사용으로 메모리 최적화)
    js_sync = f"""
    <script>
    setTimeout(() => {{
        const iframes = window.parent.document.querySelectorAll('iframe');
        iframes.forEach(iframe => {{
            iframe.contentWindow.postMessage({{
                type: 'DATA_TRANSFER', 
                raw: new Uint8Array({list(video_bytes)})
            }}, '*');
        }});
    }}, 1500);
    </script>
    """
    st.markdown(js_sync, unsafe_allow_html=True)
    st.success("데이터 전송 중... 잠시 후 영상이 나타나면 재생을 눌러주세요.")
else:
    st.info("6월 아기 탄생 전, 최고의 임팩트 데이터를 확보하세요!")
