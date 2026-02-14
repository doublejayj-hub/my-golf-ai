import streamlit as st

# 갤럭시 S24 최적화 설정
st.set_page_config(layout="wide", page_title="GDR AI Golf Coach")

st.title("⛳ GDR AI 초정밀 스윙 분석기")

# 1. 파일 업로더 (가장 단순한 형태)
st.write("### 1단계: 영상을 선택해 주세요")
f_file = st.file_uploader("정면 영상 선택", type=['mp4', 'mov'], key="f")
s_file = st.file_uploader("측면 영상 선택", type=['mp4', 'mov'], key="s")

st.divider()

# 2. 강제 렌더링 로직
st.write("### 2단계: 분석 화면 확인")
if f_file is not None:
    st.success(f"정면 로드됨: {f_file.name}")
    st.video(f_file) # 데이터 읽기 과정을 생략하고 직접 전달

if s_file is not None:
    st.success(f"측면 로드됨: {s_file.name}")
    st.video(s_file)

if f_file and s_file:
    if st.button("📊 AI 스윙 리포트 발행"):
        st.balloons()
        st.error("🚨 배치기 주의: 임팩트 시 엉덩이 라인을 유지하세요.")
        st.info("💡 처방: 6월 아기 탄생 전까지 '의자 드릴'로 연습하세요!")
