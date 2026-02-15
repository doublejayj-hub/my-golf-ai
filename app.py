import streamlit as st
import streamlit.components.v1 as components
import base64

# [1] 자바스크립트 엔진: 중괄호와 따옴표 충돌을 막기 위해 일반 문자열로 정의
# f-string을 쓰지 않아 파이썬이 문법 에러를 낼 여지가 없습니다.
JS_LOGIC = """
<div id="w" style="width:100%; background:#000; border-radius:10px; overflow:hidden; position:relative;">
    <video id="v" controls playsinline style="width:100%; display:block; height:auto;"></video>
    <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
    <div id="st" style="position:absolute; top:10px; left:10px; color:#fff; background:rgba(255,0,0,0.8); padding:8px; font-family:monospace; border-radius:5px; font-weight:bold; z-index:100; display:none;">HYPER-RES (120FPS+)</div>
</div>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils"></script>
<script>
    const v=document.getElementById('v'), c=document.getElementById('c'), ctx=c.getContext('2d'), st=document.getElementById('st');
    let pL=null, pY=0;
    const pose=new Pose({locateFile:(f)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${f}`});
    pose.setOptions({modelComplexity:1, smoothLandmarks:true, minDetectionConfidence:0.5, minTrackingConfidence:0.5});
    
    function lerp(a,b,t){return {x:a.x+(b.x-a.x)*t, y:a.y+(b.y-a.y)*t};}

    pose.onResults((r)=>{
        if(!r.poseLandmarks) return;
        c.width=v.videoWidth; c.height=v.videoHeight;
        ctx.save(); ctx.clearRect(0,0,c.width,c.height);
        const w=r.poseLandmarks[15], h=r.poseLandmarks[23], vy=w.y-pY;
        const isI = (vy>0.01 && w.y<h.y+0.2)||(w.y>=h.y-0.1 && w.y<=h.y+0.3);
        if(isI && pL){
            st.style.display="block";
            [0.25, 0.5, 0.75].forEach(t=>{
                const mid=r.poseLandmarks.map((l,i)=>lerp(pL[i],l,t));
                drawConnectors(ctx,mid,POSE_CONNECTIONS,{color:"rgba(0,255,255,0.4)",lineWidth:1});
            });
        }else{st.style.display="none";}
        drawConnectors(ctx,r.poseLandmarks,POSE_CONNECTIONS,{color:'#00FF00',lineWidth:4});
        drawLandmarks(ctx,r.poseLandmarks,{color:'#FF0000',lineWidth:2,radius:5});
        pL=r.poseLandmarks; pY=w.y; ctx.restore();
    });

    // 영상 소스 주입
    v.src = "VIDEO_DATA_URI";
    async function loop(){if(!v.paused&&!v.ended){await pose.send({image:v});}requestAnimationFrame(loop);}
    v.onplay=loop;
</script>
"""

st.set_page_config(layout="wide")
st.title("⛳ GDR AI 초정밀 분석기 (재생 안정화 버전)")

f = st.file_uploader("분석할 영상을 업로드하세요", type=['mp4', 'mov'])

if f:
    # 1. 영상 데이터 처리 (가장 확실한 재생 방식)
    v_b64 = base64.b64encode(f.read()).decode()
    v_src = "data:video/mp4;base64," + v_b64
    
    # 2. [핵심] 템플릿 치환 시 f-string을 쓰지 않고 단순 문자열 replace만 사용
    # 이렇게 하면 파이썬이 전체 코드를 해석하려다 에러를 낼 일이 없습니다.
    final_html = JS_LOGIC.replace("VIDEO_DATA_URI", v_src)
    
    # 3. 컴포넌트 출력
    components.html(final_html, height=600)
    st.success("✅ 재생 엔진 준비 완료! 재생 버튼을 눌러주세요.")
else:
    st.info("6월 아기 탄생 전, 최고의 임팩트 수치를 확보하세요!")
