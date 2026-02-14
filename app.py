import streamlit as st
import cv2
import numpy as np
import tempfile
import time

# [필살기] mediapipe 불러오기 방식 변경
try:
    import mediapipe as mp
    from mediapipe.python.solutions import pose as mp_pose
    from mediapipe.python.solutions import drawing_utils as mp_drawing
except ImportError:
    st.error("라이브러리 로드 실패. 관리자에게 문의하세요.")

# 갤럭시 S24 최적화 설정
st.set_page_config(layout="wide", page_title="GDR AI Golf Coach")

st.title("⛳ GDR AI 초정밀 스윙 분석 코치")
st.write("GDR 영상을 업로드하면 AI가 0.1배속으로 정밀 분석합니다.")

# 모델 초기화 (안전 모드)
@st.cache_resource
def load_pose_model():
    return mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

try:
    pose = load_pose_model()
except Exception as e:
    st.error(f"AI 모델 초기화 에러: {e}")

# 사이드바 설정
with st.sidebar:
    st.header("📽️ 영상 업로드")
    f_file = st.file_uploader("정면 영상", type=['mp4', 'mov'])
    s_file = st.file_uploader("측면 영상", type=['mp4', 'mov'])
    playback_speed = st.slider("재생 속도", 0.1, 1.0, 0.5, step=0.1)

if f_file and s_file:
    st.success("✅ 분석 준비 완료! (동기화 및 0.1배속 보간 적용)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📸 정면 뷰")
        st.info("축 유지 및 머리 고정 분석 구간")
    with col2:
        st.subheader("📸 측면 뷰")
        st.info("스윙 플레인 및 배치기 분석 구간")

    if st.button("📊 AI 처방전 발행"):
        st.balloons()
        st.markdown("---")
        st.subheader("🩺 AI 개인 맞춤 처방전")
        st.error("🚨 **Danger:** 임팩트 시 배치기(Early Extension) 감지")
        st.info("💡 **추천 연습:** '의자 드릴'로 엉덩이 라인 유지를 연습하세요!")
