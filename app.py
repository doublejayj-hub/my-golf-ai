import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import tempfile
import google.generativeai as genai
import os

# [1] Gemini 보안 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error("Gemini API 키 설정을 확인해주세요.")
    st.stop()

# [2] MediaPipePose 솔루션 초기화 (표준 방식)
mp_pose = mp.solutions.pose
pose_engine = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.5
)

st.set_page_config(layout="centered", page_title="GDR AI v26")
st.title("⛳ GDR AI Pro: 서버 사이드 분석 v26.0")

# [3] 파일 업로드
f = st.file_uploader("스윙 영상을 업로드하세요 (MP4/MOV)", type=['mp4', 'mov'])

if f:
    # 임시 파일 생성 및 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tfile:
        tfile.write(f.read())
        temp_path = tfile.name

    try:
        with st.spinner("서버에서 물리 데이터를 정밀 분석 중입니다..."):
            cap = cv2.VideoCapture(temp_path)
            spine_angles = []
            
            # 성능 최적화: 3프레임당 1회 스캔
            frame_count = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret: break
                
                if frame_count % 3 == 0:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = pose_engine.process(frame_rgb)
                    
                    if results.pose_landmarks:
                        lm = results.pose_landmarks.landmark
                        # 어깨 및 골반 중앙점 계산
                        sh_y = (lm[mp_pose.PoseLandmark.LEFT_SHOULDER].y + lm[mp_pose.PoseLandmark.RIGHT_SHOULDER].y) / 2
                        sh_x = (lm[mp_pose.PoseLandmark.LEFT_SHOULDER].x + lm[mp_pose.PoseLandmark.RIGHT_SHOULDER].x) / 2
                        h_y = (lm[mp_pose.PoseLandmark.LEFT_HIP].y + lm[mp_pose.PoseLandmark.RIGHT_HIP].y) / 2
                        h_x = (lm[mp_pose.PoseLandmark.LEFT_HIP].x + lm[mp_pose.PoseLandmark.RIGHT_HIP].x) / 2
                        
                        # 척추 기울기(라디안 -> 도)
                        angle = np.abs(np.arctan2(h_y - sh_y, h_x - sh_x) * 180 / np.pi)
                        spine_angles.append(angle)
                frame_count += 1
            cap.release()

        if spine_angles:
            s_delta = round(max(spine_angles) - min(spine_angles), 1)
            st.success(f"✅ 분석 완료! 척추각 편차: {s_delta}°")
            
            # [4] Gemini AI 리포트 생성 (6월 아빠 격려 포함)
            st.divider()
            st.header("📋 AI 지능형 역학 리포트")
            
            with st.spinner("Gemini Pro가 분석 리포트를 작성 중입니다..."):
                prompt = f"""
                당신은 세계적인 골프 물리 역학 전문가입니다. 
                분석된 척추각 편차: {s_delta}도.
                1. 이 데이터가 암시하는 '배치기(Early Extension)' 및 축 안정성 문제를 전문적으로 설명하세요.
                2. 6월에 태어날 아기에게 멋진 아빠가 될 수 있도록 따뜻한 응원을 포함하세요.
                한국어로 답변해주세요.
                """
                response = model.generate_content(prompt)
                st.chat_message("assistant").write(response.text)
                
            st.divider()
            st.subheader("📺 추천 교정 레슨")
            yt_link = "https://www.youtube.com/watch?v=VrOGGXdf_tM" if s_delta > 4 else "https://www.youtube.com/watch?v=2vT64W2XfC0"
            st.video(yt_link)
        else:
            st.error("영상에서 인체 랜드마크를 찾을 수 없습니다. 전신이 잘 보이는 영상을 사용해 주세요.")

    except Exception as e:
        st.error(f"분석 중 오류 발생: {e}")
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

st.sidebar.markdown(f"**Baby Due: June 2026** 👶")
