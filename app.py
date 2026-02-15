import streamlit as st
import streamlit.components.v1 as components
import base64

# [1] AI 분석 엔진 공용 템플릿 (f-string 에러 방지를 위해 일반 문자열 유지)
HTML_TEMPLATE = """
<div style="width:100%; background:#000; border-radius:10px; overflow:hidden; position:relative;">
    <video id="v" controls playsinline style="width:100%; display:block; height:auto;"></video>
    <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
    <div style="position:absolute; bottom:50px; left:0; width:100%; background:rgba(0,0,0,0.5); color:#0f0; padding:5px 15px; font-family:monospace; z-index:100; display:flex; justify-content:space-between; font-size:12px;">
        <span>VIEW: LABEL_HERE</span>
        <span>SPINE: <b id="s_v">0.0</b>°</span>
        <span>KNEE: <b id="k_v">0.0</b>°</span>
        <span id="md" style="color:#ff0;">STD</span>
    </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils"></script>
<script>
    const v=document.getElementById('v'), c=document.getElementById('c'), ctx=c.getContext('2d');
    const sD=document.getElementById('s_v'), kD=document.getElementById('k_v'), mD=document.getElementById('md');
    let pL=null, pY=0;

    const pose=new Pose({locateFile:(path)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${path}`});
    pose.setOptions({modelComplexity:1, smoothLandmarks:true, minDetectionConfidence:0.5, minTrackingConfidence:0.5});
    
    function lerp(a,b,t){return {x:a.x+(b.x-a.x)*t, y:a.y+(b.y-a.y)*t};}
    function getAng(p1, p2){return Math.abs(Math.atan2(p2.y-p1.y, p2.x-p1.x)*180/Math.PI);}

    pose.onResults((r)=>{
        if(!r.poseLandmarks) return;
        c.width=v.videoWidth; c.height=v.videoHeight;
        ctx.save(); ctx.clearRect(0,0,c.width,c.height);
        const w=r.poseLandmarks[15], h=r.poseLandmarks[23], sh=r.poseLandmarks[11], k=r.poseLandmarks[25];
        sD.innerText = getAng(sh, h).toFixed(1);
        kD.innerText = getAng(h, k).toFixed(1);
        const isI = (w.y-pY > 0.01 && w.y<h.y+0.2)||(w.y>=h.y-0.1 && w.y<=h.y+0.3);
        if(isI && pL){
            mD.innerText="HYPER"; mD.style.color="#f00";
            [0.5].forEach(t=>{
                const mid=r.poseLandmarks.map((l,i)=>lerp(pL[i],l,t));
                drawConnectors(ctx,mid,POSE_CONNECTIONS,{color:"rgba(0,255,255,0.4)",lineWidth:1});
            });
        } else { mD.innerText="STD"; mD.style.color="#ff0"; }
        drawConnectors(ctx,r.poseLandmarks,POSE_CONNECTIONS,{color:'#00FF00',lineWidth:3});
        drawLandmarks(ctx,r.poseLandmarks,{color:'#FF0000',lineWidth:1,radius:3});
        pL=r.poseLandmarks; pY=w.y; ctx.restore();
    });
    v.src = "VIDEO_SRC_HERE";
    v.onplay = async function(){ while(!v.paused && !v.ended){ await pose.send({image:v}); await new Promise(res=>requestAnimationFrame(res)); } };
</script>
"""

st.set_page_config(layout="wide")
st.title("⛳ GDR AI 정면/측면 통합 분석 엔진")

# [2] 탭 구성 - 업로드 UI와 분석기 출력 로직 정밀 결합
tab1, tab2, tab3 = st.tabs(["🎥 정면 분석 (Front)", "🎥 측면 분석 (Side)", "📊 종합 분석 리포트"])

with tab1:
    st.subheader("정면 스윙 업로드")
    f_front = st.file_uploader("영상을 선택하세요", type=['mp4', 'mov'], key="up_front")
    if f_front:
        v_src = f"data:video/mp4;base64,{base64.b64encode(f_front.read()).decode()}"
        # LABEL_HERE와 VIDEO_SRC_HERE를 정면에 맞춰 치환
        html_front = HTML_TEMPLATE.replace("VIDEO_SRC_HERE", v_src).replace("LABEL_HERE", "FRONT")
        components.html(html_front, height=500)

with tab2:
    st.subheader("측면 스윙 업로드")
    # [수정] 측면 탭에서도 업로드 UI가 확실히 나오도록 명시
    f_side = st.file_uploader("영상을 선택하세요", type=['mp4', 'mov'], key="up_side")
    if f_side:
        v_src = f"data:video/mp4;base64,{base64.b64encode(f_side.read()).decode()}"
        # LABEL_HERE와 VIDEO_SRC_HERE를 측면에 맞춰 치환
        html_side = HTML_TEMPLATE.replace("VIDEO_SRC_HERE", v_src).replace("LABEL_HERE", "SIDE")
        components.html(html_side, height=500)

with tab3:
    st.subheader("📝 AI 스윙 종합 리포트")
    if f_front or f_side:
        col1, col2 = st.columns(2)
        with col1:
            st.info("🎯 **정면(Front)**: 임팩트 가속도와 하체 고정 위주 분석")
        with col2:
            st.info("🎯 **측면(Side)**: 척추각 유지 및 스윙 궤도 위주 분석")
        st.divider()
        st.success("6월 아빠가 되기 전, 완벽한 스윙 밸런스를 구축하세요! 👶")
    else:
        st.warning("영상을 업로드하면 AI가 실시간 물리 연산 리포트를 생성합니다.")
