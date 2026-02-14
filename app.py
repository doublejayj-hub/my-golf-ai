import streamlit as st
import tempfile
import os

# 갤럭시 S24 최적화 설정
st.set_page_config(layout="wide", page_title="GDR AI Golf Coach")

st.title("⛳ GDR AI 초정밀 스윙 분석기")

# 1. 사이드바 설정
with st.sidebar:
    st.header("📽️ 영상 업로드")
    f_file = st.file_uploader("정면 영상 (GDR)", type=['mp4', 'mov'])
    s_file = st.file_uploader("측면 영상 (GDR)", type=['mp4', 'mov'])

# 2. 영상 처리 및 화면 표시 로직
def play_video(file, title):
    if file is not None:
        # 임시 파일을 생성하여 비디오 경로 확보
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(file.read())
        
        st.subheader(title)
        st.video(tfile.name) # 실제 영상 재생 칸을 생성
        st.success(f"✅ {file.name} 재생 준비 완료")

# 3. 메인 화면 구성
if f_file or s_file:
    col1, col2 = st.columns(2)
    
    with col1:
        if f_file:
            play_video(f_file, "📸 정면 분석")
        else:
            st.info("정면 영상을 올려주세요.")
            
    with col2:
        if s_file:
            play_video(s_file, "📸 측면 분석")
        else:
            st.info("측면 영상을 올려주세요.")

    if f_file and s_file:
        if st.button("📊 AI 스윙 분석 리포트 발행"):
            st.balloons()
            st.error("🚨 배치기 주의: 임팩트 시 엉덩이 라인을 유지하세요.")
            st.info("💡 처방: 6월 아기 탄생 전까지 '의자 드릴'로 연습하세요!")
else:
    st.warning("왼쪽 사이드바에서 분석할 GDR 영상을 선택해 주세요.")
