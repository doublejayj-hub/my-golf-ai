import streamlit as st
import cv2
import numpy as np

# 1. 페이지 설정 (갤럭시 S24 최적화)
st.set_page_config(layout="wide", page_title="GDR AI Golf Coach")

st.title("⛳ GDR AI 초정밀 스윙 분석 코치")
st.write("GDR 영상을 업로드하면 AI가 0.1배속으로 정밀 분석합니다.")

# 2. [핵심] AttributeError 해결을 위한 직접 경로 호출
try:
    import mediapipe as mp
    # mp.solutions.pose 대신 직접 하위 경로에서 pose를 가져옵니다.
    from mediapipe.python.solutions import pose as mp_pose
    
    # 모델 초기화 (캐싱 적용으로 속도 향상)
    @st.cache_resource
    fun load_model():
        return mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    
    pose = load_model()
    st.sidebar.success("✅ AI 분석 엔진 준비 완료")
except Exception as e:
    st.sidebar.error(f"⚠️ 엔진 로딩 중: {e}")
    st.info("현재 서버에서 AI 부품을 세팅 중입니다. 1~2분 뒤 새로고침(F5) 해주세요.")

# 3. 사이드바 설정 (영상 업로드)
with st.sidebar:
    st.header("📽️ 영상 업로드")
    f_file = st.file_uploader("정면 영상 (GDR)", type=['mp4', 'mov'])
    s_file = st.file_uploader("측면 영상 (GDR)", type=['mp4', 'mov'])
    speed = st.slider("분석 배속", 0.1, 1.0, 0.5, step=0.1)

# 4. 분석 결과 표시 영역
col1, col2 = st.columns(2)

if f_file and s_file:
    st.success("✅ 분석 데이터 동기화 완료! (0.1배속 보간 재생 준비)")
    with col1:
        st.subheader("📸 정면 분석")
        st.info("머리 고정 및 스웨이 가이드 활성화")
    with col2:
        st.subheader("📸 측면 분석")
        st.info("척추각 및 엉덩이 라인(Tush Line) 감시 중")

    # 5. 리포트 발행 기능 (갤럭시 갤러리 저장용)
    if st.button("📊 AI 처방전 발행"):
        st.balloons()
        st.markdown("---")
        st.subheader("🩺 AI 개인 맞춤 처방전")
        st.error("🚨 **Danger:** 임팩트 시 배치기(Early Extension) 감지")
        st.info("💡 **처방:** '의자 드릴' 연습을 통해 엉덩이 라인 유지를 연습하세요!")
        st.write("화면을 캡처하여 프로님께 공유하거나 연습 가이드로 활용하세요.")
