import streamlit as st

# 갤럭시 S24 최적화 설정
st.set_page_config(layout="wide", page_title="GDR AI Golf Coach")

st.title("⛳ GDR AI 초정밀 스윙 분석기")
st.write("측면 로드 성공! 이제 정면 영상도 깨워보겠습니다.")

# 1. 파일 업로더 (고유 키값 부여로 인식력 강화)
col1, col2 = st.columns(2)

with col1:
    st.write("### 📸 정면 뷰")
    # key값을 변경하여 브라우저가 새 업로더로 인식하게 함
    f_file = st.file_uploader("정면 파일을 선택하세요", type=['mp4', 'mov'], key="front_v2")
    if f_file:
        st.success(f"정면 인식됨: {f_file.name}")
        st.video(f_file)

with col2:
    st.write("### 📸 측면 뷰")
    s_file = st.file_uploader("측면 파일을 선택하세요", type=['mp4', 'mov'], key="side_v2")
    if s_file:
        st.success(f"측면 인식됨: {s_file.name}")
        st.video(s_file)

st.divider()

# 2. 리포트 발행 기능
if f_file and s_file:
    if st.button("📊 AI 스윙 리포트 발행"):
        st.balloons()
        st.error("🚨 배치기 주의: 임팩트 시 엉덩이 라인을 유지하세요.")
        st.info("💡 처방: 6월 아기 탄생 전 '의자 드릴' 연습 필수!")
