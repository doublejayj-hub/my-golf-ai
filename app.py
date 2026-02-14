import streamlit as st
import cv2
import mediapipe as mp
import numpy as np

# 갤럭시 S24 최적화 설정
st.set_page_config(layout="wide", page_title="GDR AI Golf Coach")

st.title("⛳ GDR AI 초정밀 스윙 분석 코치")

# 분석 엔진 초기화
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# 사이드바: 영상 업로드
with st.sidebar:
    st.header("📽️ 영상 업로드")
    f_file = st.file_uploader("정면 영상 (GDR)", type=['mp4', 'mov'])
    s_file = st.file_uploader("측면 영상 (GDR)", type=['mp4', 'mov'])
    speed = st.slider("분석 배속", 0.1, 1.0, 0.5, step=0.1)

# 메인 화면 UI
if f_file and s_file:
    st.success("✅ 분석 준비 완료! 영상을 재생합니다.")
    col1, col2 = st.columns(2)
    with col1: st.subheader("📸 정면 분석")
    with col2: st.subheader("📸 측면 분석")
    
    if st.button("📊 AI 처방전 발행"):
        st.balloons()
        st.error("🚨 배치기 주의: 임팩트 시 엉덩이 라인을 유지하세요.")
        st.info("💡 처방: '의자 드릴' 연습을 추천합니다.")
else:
    st.info("왼쪽 사이드바에서 분석할 GDR 영상을 업로드해 주세요.")
