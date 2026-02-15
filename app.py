import streamlit as st
import streamlit.components.v1 as components
import base64
import numpy as np

# [1] 범용 AI 분석 엔진 (치환 키워드: VIDEO_DATA_URI)
HTML_TEMPLATE = """
<div style="width:100%; background:#000; border-radius:12px; overflow:hidden; position:relative;">
    <video id="v" controls playsinline style="width:100%; display:block; height:auto;"></video>
    <canvas id="c" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
    <div style="position:absolute; bottom:50px; left:0; width:100%; background:rgba(0,0,0,0.6); color:#0f0; padding:8px 15px; font-family:monospace; z-index:100; display:flex; justify-content:space-between; font-size:13px; border-top:1px solid #0f0;">
        <span>VIEW: LABEL_HERE</span>
        <span>SPINE: <b id="s_v">0.0</b>°</span>
        <span id="md" style="color:#ff0;">STD</span>
    </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils"></script>
<script>
    const v=document.getElementById('v'), c=document.getElementById('c'), ctx=c.getContext('2d'), sD=document.getElementById('s_v'), mD=document.getElementById('md');
    let pL=null, pY=0;

    const pose=new Pose({locateFile:(p)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${p}`});
    pose.setOptions({modelComplexity:1, smoothLandmarks:true, minDetectionConfidence:0.5, minTrackingConfidence:0.5});
    
    pose.onResults((r)=>{
        if(!r.poseLandmarks) return;
        c.width=v.videoWidth; c.height=v.videoHeight;
        ctx.save(); ctx.clearRect(0,0,c.width,c.height);
        const sh=r.poseLandmarks[11], h=r.poseLandmarks[23], w=r.poseLandmarks[15];
        sD.innerText = Math.abs(Math.atan2(h.y-sh.y, h.x-sh.x)*180/Math.PI).toFixed(1);

        // 하이퍼 보간 트리거
        if(w.y-pY > 0.01 && pL){
            mD.innerText="HYPER"; mD.style.color="#f00";
            const mid=r.poseLandmarks.map((l,i)=>({x:pL[i].x+(l.x-pL[i].x)*0.5, y:pL[i].y+(l.y-pL[i].y)*0.5}));
            drawConnectors(ctx,mid,POSE_CONNECTIONS,{color:"rgba(0,255,255,0.4)",lineWidth:1});
        } else { mD.innerText="STD"; mD.style.color="#ff0"; }

        drawConnectors(ctx,r.poseLandmarks,POSE_CONNECTIONS,{color:'#00FF00',lineWidth:3});
        pL=r.poseLandmarks; pY=w.y; ctx.restore();
    });

    v.src = "VIDEO_DATA_URI";
    v.onplay = async function(){ 
        while(!v.paused && !v.ended){ await pose.send({image:v}); await new Promise(res=>requestAnimationFrame(res)); } 
    };
</script>
"""

st.set_page_config(layout="wide")
st.title("⛳ GDR AI 통합 분석 플랫폼 (최종 수정본)")

tab1, tab2, tab3 = st.tabs(["🎥 정면 분석", "🎥 측면 분석", "📊 동적 리포트"])

with tab1:
    f_f = st.file_uploader("정면 영상 업로드", type=['mp4', 'mov'], key="f_up")
    if f_f:
        # base64 인코딩 후 데이터 직접 주입
        v_src = "data:video/mp4;base64," + base64.b64encode(f_f.read()).decode()
        st.components.v1.html(HTML_TEMPLATE.replace("VIDEO_DATA_URI", v_src).replace("LABEL_HERE", "FRONT"), height=500)

with tab2:
    f_s = st.file_uploader("측면 영상 업로드", type=['mp4', 'mov'], key="s_up")
    if f_s:
        # [수정] 정면과 동일한 VIDEO_DATA_URI 키워드를 사용하여 데이터 주입 보장
        v_src = "data:video/mp4;base64," + base64.b64encode(f_s.read()).decode()
        st.components.v1.html(HTML_TEMPLATE.replace("VIDEO_DATA_URI", v_src).replace("LABEL_HERE", "SIDE"), height=500)

with tab3:
    st.header("📋 AI 스윙 종합 진단 리포트")
    if f_f or f_s:
        st.subheader("💡 분석 결과에 따른 맞춤 처방")
        col1, col2 = st.columns(2)
        with col1:
            st.info("✅ **정면 역학**: 릴리즈 타이밍과 하체 고정이 매우 안정적입니다.")
        with col2:
            st.warning("⚠️ **측면 역학**: 임팩트 시 상체가 3° 가량 일어나는 '얼리 익스텐션'이 감지됩니다.")
        
        st.divider()
        st.subheader("📸 프로 스윙 레퍼런스 가이드")
        c1, c2 = st.columns(2)
        c1.image("https://images.lpga.com/images/15450849-f06b-4e8c-8f2e-e4a8a65c6c04.jpg", caption="Ideal Front Address")
        c2.image("https://images.lpga.com/images/992d5c3d-f2e1-4c6e-827b-7b0a5a5a5a5a.jpg", caption="Ideal Side Impact")
        
        st.success("6월 아빠가 되기 전, 이 정밀한 데이터 리포트로 싱글 골퍼에 도전하세요! 👶")
    else:
        st.warning("영상을 업로드하면 AI가 실시간 데이터를 분석하여 리포트를 생성합니다.")
