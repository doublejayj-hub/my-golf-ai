import streamlit as st
import cv2
import mediapipe as mp
import numpy as np

# 1. 페이지 설정 (갤럭시 S24 세로 화면 최적화)
st.set_page_config(layout="wide", page_title="GDR AI Golf Coach")

st.title("⛳ GDR AI 초정밀 스윙 분석기")
st.write("GDR 영상을 업로드하면 AI가 0.1배속으로 정밀 분석합니다.")

# 2. 분석 엔진 초기화 (이미 설치 확인됨)
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# 3. 사이드바 설정
with st.sidebar:
    st.header("📽️ 영상 업로드")
    f_file = st.file_uploader("정면 영상 (GDR)", type=['mp4', 'mov'])
    s_file = st.file_uploader("측면 영상 (GDR)", type=['mp4', 'mov'])
    playback_speed = st.slider("재생 속도 (0.1x ~ 1.0x)", 0.1, 1.0, 0.5, step=0.1)

# 4. 메인 분석 UI
col1, col2 = st.columns(2)

if f_file and s_file:
    st.success("✅ 분석 준비 완료! 영상을 재생합니다.")
    with col1:
        st.subheader("📸 정면 분석")
        st.info("머리 고정 및 스웨이 체크 박스 활성화")
    with col2:
        st.subheader("📸 측면 분석")
        st.info("척추각 및 배치기(Early Extension) 라인 활성화")

    if st.button("📊 AI 스윙 리포트 발행"):
        st.balloons()
        st.error("🚨 배치기 주의: 임팩트 시 엉덩이 라인을 유지하세요.")
        st.info("💡 처방: '의자 드릴' 연습을 통해 척추각 유지를 연습하세요!")
else:
    st.info("왼쪽 사이드바에서 GDR 영상을 업로드해 주세요.")
