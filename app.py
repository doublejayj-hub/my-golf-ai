import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import tempfile
import google.generativeai as genai
import os

# [1] Gemini 및 MediaPipe 초기화
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-pro')
except:
    st.error("API 키 설정을 확인하세요.")
    st.stop()

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, model_complexity=1)

st.set_page_config(layout="centered", page_title="GDR AI v25")
st.title("⛳ GDR AI Pro: 서버 사이드 분석 v25.0")

# [2] 파일 업로드
f = st.file_uploader("스윙 영상 업로드 (MP4/MOV)", type=['mp4', 'mov'])

if f:
    # 임시 파일 저장 (서버가 읽기 위함)
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(f.read())
    
    with st.spinner("서버에서 영상을 정밀 분석 중입니다..."):
        cap = cv2.VideoCapture(tfile.name)
        spine_angles = []
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            # 성능을 위해 프레임 리사이징 및 RGB 변환
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(frame_rgb)
            
            if results.pose_landmarks:
                # 척추각 계산 (어깨 중앙과 골반 중앙 좌표 활용)
                lm = results.pose_landmarks.landmark
                sh_y = (lm[mp_pose.PoseLandmark.LEFT_SHOULDER].y + lm[mp_pose.PoseLandmark.RIGHT_SHOULDER].y) / 2
                sh_x = (lm[mp_pose.PoseLandmark.LEFT_SHOULDER].x + lm[mp_pose.PoseLandmark.RIGHT_SHOULDER].x) / 2
                h_y = (lm[mp_pose.PoseLandmark.LEFT_HIP].y + lm[mp_pose.PoseLandmark.RIGHT_HIP].y) / 2
                h_x = (lm[mp_pose.PoseLandmark.LEFT_HIP].x + lm[mp_pose.PoseLandmark.RIGHT_HIP].x) / 2
                
                angle = np.abs(np.arctan2(h_y - sh_y, h_x - sh_x) * 180 / np.pi)
                spine_angles.append(angle)
        
        cap.release()
        
        if spine_angles:
            s_delta = round(max(spine_angles) - min(spine_angles), 1)
            
            # [3] 결과 표시 및 Gemini 분석
            st.success(f"✅ 분석 완료! 측정된 척추각 편차: {s_delta}°")
            
            st.divider()
            st.header("📋 AI 지능형 역학 리포트")
            
            with st.spinner("Gemini Pro가 분석 리포트를 작성 중입니다..."):
                prompt = f"""
                당신은 골프 역학 전문가입니다. 척추각 편차 {s_delta}도인 골퍼를 위해:
                1. 이 수치가 암시하는 운동학적 문제(배치기 등)를 역학적으로 설명할 것.
                2. 6월에 아빠가 될 골퍼를 위해 따뜻한 응원을 포함할 것.
                한국어로 답변해줘.
                """
                response = model.generate_content(prompt)
                st.chat_message("assistant").write(response.text)
                
            st.divider()
            st.subheader("📺 추천 교정 레슨")
            st.video("https://www.youtube.com/watch?v=VrOGGXdf_tM" if s_delta > 4 else "https://www.youtube.com/watch?v=2vT64W2XfC0")
            
        else:
            st.error("영상에서 뼈대를 추출하지 못했습니다. 정면 또는 측면 전신이 보이는 영상을 사용해 주세요.")
            
    os.unlink(tfile.name) # 임시 파일 삭제

st.sidebar.markdown(f"**Baby Due: June 2026** 👶")
