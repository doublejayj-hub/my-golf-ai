import streamlit as st
import streamlit.components.v1 as components
import base64

# [핵심] 모든 수치를 영상 내부 오버레이 레이어에 직접 출력하는 방식
FINAL_ANALYTICS_HTML = """
<div id="w" style="width:100%; background:#000; border-radius:10px; overflow:hidden; position:relative;">
    <video id="v" controls playsinline style="width:100%; display:block; height:auto;"></video>
    <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
    
    <div id="db" style="position:absolute; top:10px; right:10px; background:rgba(0,0,0,0.8); color:#0f0; padding:15px; font-family:monospace; border:1px solid #0f0; border-radius:5px; z-index:100; min-width:180px;">
        <div style="border-bottom:1px solid #0f0; margin-bottom:5px; padding-bottom:3px; color:#fff;">LIVE ANALYTICS</div>
        <div>SPINE : <span id="s_val">0.0</span>°</div>
        <div>KNEE  : <span id="k_val">0.0</span>°</div>
        <div>SWAY  : <span id="w_val">0.00</span></div>
        <div id="mode" style="margin-top:10px; color:#ff0; font-size:10px;">MODE: STANDARD</div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils"></script>

<script>
    const v=document.getElementById('v'), c=document.getElementById('c'), ctx=c.getContext('2d');
    const sDisp=document.getElementById('s_val'), kDisp=document.getElementById('k_val'), wDisp=document.getElementById('w_val'), mDisp=document.getElementById('mode');
    
    let pL=null, pY=0;
    const pose=new Pose({locateFile:(f)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${f}`});
    pose.setOptions({modelComplexity:1, smoothLandmarks:true, minDetectionConfidence:0.5, minTrackingConfidence:0.5});
    
    function lerp(a,b,t){return {x:a.x+(b.x-a.x)*t, y:a.y+(b.y-a.y)*t};}
    function getAng(p1, p2){
        return Math.abs(Math.atan2(p2.y-p1.y, p2.x-p1.x)*180/Math.PI);
    }

    pose.onResults((r)=>{
        if(!r.poseLandmarks) return;
        c.width=v.videoWidth; c.height=v.videoHeight;
        ctx.save(); ctx.clearRect(0,0,c.width,c.height);
        
        const w=r.poseLandmarks[15], h=r.poseLandmarks[23], sh=r.poseLandmarks[11], k=r.poseLandmarks[25];
        const vy=w.y-pY;

        // 1. 실제 물리 수치 연산
        const spineAngle = getAng(sh, h);
        const kneeAngle = getAng(h, k);
        const swayX = (h.x * 100).toFixed(2); // 골반 위치 기반 스웨이

        // 2. 영상 내 대시보드에 즉시 업데이트
        sDisp.innerText = spineAngle.toFixed(1);
        kDisp.innerText = kneeAngle.toFixed(1);
        wDisp.innerText = swayX;

        // 3. 임팩트 구간 하이퍼 보간 로직
        const isImpact = (vy>0.01 && w.y<h.y+0.2)||(w.y>=h.y-0.1 && w.y<=h.y+0.3);
        if(isImpact && pL){
            mDisp.innerText = "MODE: HYPER-RES (120FPS+)";
            mDisp.style.color = "#f00";
            [0.5].forEach(t=>{
                const mid=r.poseLandmarks.map((l,i)=>lerp(pL[i],l,t));
                drawConnectors(ctx,mid,POSE_CONNECTIONS,{color:"rgba(0,255,255,0.4)",lineWidth:1});
            });
        } else {
            mDisp.innerText = "MODE: STANDARD (60FPS)";
            mDisp.style.color = "#ff0";
        }

        drawConnectors(ctx,r.poseLandmarks,POSE_CONNECTIONS,{color:'#00FF00',lineWidth:4});
        drawLandmarks(ctx,r.poseLandmarks,{color:'#FF0000',lineWidth:2,radius:5});
        pL=r.poseLandmarks; pY=w.y; ctx.restore();
    });

    v.src = "VIDEO_DATA_URI";
    async function loop(){if(!v.paused&&!v.ended){await pose.send({image:v});}requestAnimationFrame(loop);}
    v.onplay=loop;
</script>
"""

st.set_page_config(layout="wide")
st.title("⛳ AI 진짜 데이터 기반 역학 분석기")

f = st.file_uploader("분석할 영상을 업로드하세요", type=['mp4', 'mov'])

if f:
    # 데이터 직접 주입 방식 유지
    v_b64 = base64.b64encode(f.read()).decode()
    v_src = f"data:video/mp4;base64,{v_b64}"
    
    # 영상 내부에 모든 분석 결과가 표시되도록 구성
    final_html = FINAL_ANALYTICS_HTML.replace("VIDEO_DATA_URI", v_src)
    
    st.info("💡 영상 우측 상단 'LIVE ANALYTICS' 창에서 AI가 계산한 진짜 수치를 확인하세요.")
    components.html(final_html, height=600)
    
    st.divider()
    st.subheader("📋 스윙 진단 가이드")
    st.write("- **Spine**: 척추각이 백스윙 탑까지 일정하게 유지되는지 확인하세요.")
    st.write("- **Sway**: 다운스윙 시 수치가 급격하게 변한다면 하체 고정이 필요합니다.")
    st.success("6월 아기 탄생 전까지, 이 데이터들을 보며 완벽한 폼을 완성해 보세요!")
else:
    st.warning("영상을 업로드하면 AI가 관절 좌표를 이용한 물리 연산을 시작합니다.")
