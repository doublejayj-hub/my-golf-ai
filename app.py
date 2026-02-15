import streamlit as st
import cv2
import mediapipe.python.solutions.pose as mp_pose # 경로를 더 명시적으로 수정
import mediapipe.python.solutions.drawing_utils as mp_drawing
import numpy as np
import tempfile
import google.generativeai as genai
import os
import base64

# [1] Gemini 보안 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error(f"API 키 설정을 확인하세요: {e}")
    st.stop()

# [2] MediaPipe Pose 엔진 초기화 (서버 사이드)
pose_engine = mp_pose.Pose(
    static_image_mode=False, 
    model_complexity=1, 
    min_detection_confidence=0.5
)

st.set_page_config(layout="centered", page_title="GDR AI v25.1")
st.title("⛳ GDR AI Pro: 서버 사이드 분석 v25.1")

# [3] 파일 업로드
f = st.file_uploader("스윙 영상 업로드 (MP4/MOV)", type=['mp4', 'mov'])

if f:
    # 임시 파일 저장
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(f.read())
    tfile.close() # 쓰기 완료 후 닫기
    
    with st.spinner("서버에서 영상을 프레임 단위로 정밀 분석 중입니다..."):
        cap = cv2.VideoCapture(tfile.name)
        spine_angles = []
        
        # 샘플링 분석 (속도 향상을 위해 2프레임당 1회 분석)
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            if frame_count % 2 == 0:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose_engine.process(frame_rgb)
                
                if results.pose_landmarks:
                    lm = results.pose_landmarks.landmark
                    # 어깨 및 골반 중앙점 계산
                    sh_y = (lm[mp_pose.PoseLandmark.LEFT_SHOULDER].y + lm[mp_pose.PoseLandmark.RIGHT_SHOULDER].y) / 2
                    sh_x = (lm[mp_pose.PoseLandmark.LEFT_SHOULDER].x + lm[mp_pose.PoseLandmark.RIGHT_SHOULDER].x) / 2
                    h_y = (lm[mp_pose.PoseLandmark.LEFT_HIP].y + lm[mp_pose.PoseLandmark.RIGHT_HIP].y) / 2
                    h_x = (lm[mp_pose.PoseLandmark.LEFT_HIP].x + lm[mp_pose.PoseLandmark.RIGHT_HIP].x) / 2
                    
                    angle = np.abs(np.arctan2(h_y - sh_y, h_x - sh_x) * 180 / np.pi)
                    spine_angles.append(angle)
            frame_count += 1
        
        cap.release()
        
        if spine_angles:
            s_delta = round(max(spine_angles) - min(spine_angles), 1)
            st.success(f"✅ 분석 완료! 측정된 척추각 편차: {s_delta}°")
            
            # [4] Gemini AI 리포트 생성
            st.divider()
            st.header("📋 AI 지능형 역학 리포트")
            
            with st.spinner("Gemini Pro가 분석 리포트를 작성 중입니다..."):
                prompt = f"""
                당신은 골프 역학 전문가입니다. 척추각 편차 {s_delta}도인 골퍼를 위해:
                1. 이 수치가 암시하는 운동학적 사슬(Kinematic Sequence)의 문제를 역학적으로 설명해줘.
                2. 6월에 아빠가 될 골퍼를 위해 따뜻한 응원을 포함할 것.
                한국어로 답변해줘.
                """
                response = model.generate_content(prompt)
                st.chat_message("assistant").write(response.text)
                
            st.divider()
            st.subheader("📺 추천 교정 레슨")
            yt_link = "https://www.youtube.com/watch?v=VrOGGXdf_tM" if s_delta > 4 else "https://www.youtube.com/watch?v=2vT64W2XfC0"
            st.video(yt_link)
        else:
            st.error("영상에서 뼈대를 추출하지 못했습니다. 전신이 잘 보이는 영상을 사용해 주세요.")
            
    os.unlink(tfile.name) # 임시 파일 정리

st.sidebar.markdown(f"**Baby Due: June 2026** 👶")
