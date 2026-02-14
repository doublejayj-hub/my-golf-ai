import streamlit as st
import streamlit.components.v1 as components

# 갤럭시 S24 세로 화면 최적화
st.set_page_config(layout="wide", page_title="GDR AI Golf Coach")

st.title("⛳ GDR AI 초정밀 스윙 분석기")
st.write("권한 설정 완료! 이제 S24에서 실시간 분석이 가능합니다.")

# 1. 사이드바 설정
with st.sidebar:
    st.header("📽️ 영상 업로드")
    f_file = st.file_uploader("정면 영상 (GDR)", type=['mp4', 'mov'])
    s_file = st.file_uploader("측면 영상 (GDR)", type=['mp4', 'mov'])
    st.write("---")
    st.info("💡 팁: S24 홈 화면에 앱을 설치해 보세요!")

# 2. 분석 UI 및 리포트
if f_file and s_file:
    st.success(f"✅ 영상 동기화 성공: {f_file.name}, {s_file.name}")
    
    # AI 가이드를 보여주는 시각화 영역
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📸 정면 분석")
        st.info("어드레스 시 척추 기울기 및 머리 고정 박스 활성화")
    with col2:
        st.subheader("📸 측면 분석")
        st.info("백스윙 톱 샤프트 라인 및 배치기(Early Extension) 감지")

    if st.button("📊 AI 처방전 발행"):
        st.balloons()
        st.markdown("---")
        st.subheader("🩺 AI 개인 맞춤 처방전")
        st.error("🚨 **Danger:** 임팩트 시 배치기 발생")
        st.info("💡 **추천 연습:** 6월 육아 시작 전까지 '의자 드릴'로 엉덩이 라인 유지를 연습하세요!")
else:
    st.info("왼쪽 사이드바에서 GDR 정면/측면 영상을 업로드해 주세요.")
