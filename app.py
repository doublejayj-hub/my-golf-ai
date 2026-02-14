import streamlit as st
import base64

# 갤럭시 S24 최적화 설정
st.set_page_config(layout="wide", page_title="GDR AI Golf Coach")

st.title("⛳ GDR AI 초정밀 스윙 분석기")

# 1. 사이드바 설정
with st.sidebar:
    st.header("📽️ 영상 업로드")
    f_file = st.file_uploader("정면 영상 (GDR)", type=['mp4', 'mov'])
    s_file = st.file_uploader("측면 영상 (GDR)", type=['mp4', 'mov'])

# 2. 영상을 브라우저가 즉시 읽을 수 있는 데이터로 변환하는 함수
def display_video(file):
    if file is not None:
        video_bytes = file.read()
        # 데이터를 Base64로 인코딩하여 브라우저에 직접 주입
        st.video(video_bytes)
        st.success(f"✅ {file.name} 로드 완료")

# 3. 메인 화면 구성
if f_file or s_file:
    col1, col2 = st.columns(2)
    
    with col1:
        if f_file:
            st.subheader("📸 정면 분석")
            display_video(f_file)
        else:
            st.info("정면 영상을 업로드해 주세요.")
            
    with col2:
        if s_file:
            st.subheader("📸 측면 분석")
            display_video(s_file)
        else:
            st.info("측면 영상을 업로드해 주세요.")

    if f_file and s_file:
        if st.button("📊 AI 스윙 분석 리포트 발행"):
            st.balloons()
            st.error("🚨 배치기 주의: 임팩트 시 엉덩이 라인을 유지하세요.")
            st.info("💡 처방: 6월 아기 탄생 전까지 '의자 드릴'로 연습하세요!")
else:
    st.warning("왼쪽 사이드바에서 분석할 GDR 영상을 선택해 주세요.")
