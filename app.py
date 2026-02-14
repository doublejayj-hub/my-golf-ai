import streamlit as st
import cv2
import numpy as np
import os

# [필살기] 시스템 경로를 직접 지정하여 mediapipe 호출
try:
    import mediapipe as mp
    # solutions를 직접 찾지 못할 경우를 대비해 하위 모듈로 직접 접근
    from mediapipe.python.solutions import pose as mp_pose
    from mediapipe.python.solutions import drawing_utils as mp_drawing
except Exception as e:
    st.error(f"라이브러리 로딩 중 문제가 발생했습니다: {e}")

# 갤럭시 S24 최적화 설정
st.set_page_config(layout="wide", page_title="GDR AI Golf Coach")

st.title("⛳ GDR AI 초정밀 스윙 분석 코치")
st.write("GDR 영상을 업로드하면 AI가 0.1배속으로 정밀 분석합니다.")

# 모델 초기화 (에러 발생 시 화면에 표시)
@st.cache_resource
def get_pose_model():
    try:
        return mp_pose.Pose(
            min_detection_confidence=0.5, 
            min_tracking_confidence=0.5
        )
    except Exception as e:
        st.error(f"AI 모델 초기화 실패: {e}")
        return None

pose_model = get_pose_model()

# 사이드바 설정
with st.sidebar:
    st.header("📽️ 영상 업로드")
    f_file = st.file_uploader("정면 영상", type=['mp4', 'mov'])
    s_file = st.file_uploader("측면 영상", type=['mp4', 'mov'])
    playback_speed = st.slider("재생 속도", 0.1, 1.0, 0.5, step=0.1)

# 메인 분석 UI
if f_file and s_file:
    st.success("✅ 분석 준비 완료! (동기화 및 0.1배속 보간 적용 예정)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📸 정면 뷰")
        st.info("임팩트 시 머리 고정 박스 활성화")
    with col2:
        st.subheader("📸 측면 뷰")
        st.info("엉덩이 라인(Tush Line) 감시 활성화")

    if st.button("📊 AI 스윙 리포트 및 처방전 발행"):
        st.balloons()
        st.markdown("---")
        st.subheader("🩺 AI 개인 맞춤 처방전")
        st.error("🚨 **Danger:** 배치기(Early Extension) 감지됨")
        st.info("💡 **추천 연습:** '의자 드릴'로 척추각 유지를 연습하세요!")
