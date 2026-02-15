import streamlit as st
import streamlit.components.v1 as components
import uuid
import base64

# 1. 페이지 설정 및 세션 관리
st.set_page_config(layout="wide", page_title="GDR AI Real-Time Coach")

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.title("⛳ GDR AI 진짜 연산 엔진 (구문 무결성 검증 버전)")

if 'f_vid' not in st.session_state:
    st.session_state.f_vid = None

tab1, tab2 = st.tabs(["📸 실시간 관절 추적", "📊 추출 데이터 로그"])

with tab1:
    f_input = st.file_uploader("분석할 영상 업로드", type=['mp4', 'mov'], key=f"v_{st.session_state.session_id}")
    
    if f_input:
        # 영상 데이터를 Base64로 인코딩
        tfile = f_input.read()
        b64_vid = base64.b64encode(tfile).decode()
        
        st.info("AI 엔진이 동작 중입니다. 재생 버튼을 눌러주세요.")

        # [디버깅] 줄바꿈에 의한 SyntaxError를 방지하기 위해 문자열을 한 줄씩 명확히 정의함
        h = '<div id="container" style="position:relative;width:100%;height:500px;background:#000;">'
        h += '<video id="v" controls style="width:100%;height:100%;"></video>'
        h += '<canvas id="c" style="position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;"></canvas>'
        h += '<div id="s" style="position:absolute;top:10px;left:10px;color:#0f0;font-family:monospace;background:rgba(0,0,0,0.7);padding:5px;z-index:10;">[AI] Ready</div></div>'
        
        j = '<script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>'
        j += '<script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils"></script>'
        j += '<script>'
        j += 'const v=document.getElementById("v"),c=document.getElementById("c"),ctx=c.getContext("2d"),s=document.getElementById("s");'
        j += 'const pose=new Pose({locateFile:(f)=>`https://cdn.jsdelivr.net/npm/@mediapipe/pose/${f}`});'
        j += 'pose.setOptions({modelComplexity:1,smoothLandmarks:true,minDetectionConfidence:0.5,minTrackingConfidence:0.5});'
        j += 'pose.onResults((r)=>{if(!r.poseLandmarks){s.innerText="[AI] No Pose";return;}s.innerText="[AI] Active";'
        j += 'c.width=v.videoWidth;c.height=v.videoHeight;ctx.save();ctx.clearRect(0,0,c.width,c.height);'
        j += 'drawConnectors(ctx,r.poseLandmarks,POSE_CONNECTIONS,{color:"#00FF00",lineWidth:4});'
        j += 'drawLandmarks(ctx,r.poseLandmarks,{color:"#FF0000",lineWidth:2,radius:5});ctx.restore();});'
        j += 'v.src="data:video/mp4;base64,' + b64_vid + '";'
        j += 'async function f(){if(!v.paused&&!v.ended){await pose.send({image:v});}requestAnimationFrame(f);}'
        j += 'v.onplay=()=>{
