import streamlit as st

st.set_page_config(layout="wide", page_title="GDR AI Golf Coach")

st.title("⛳ GDR AI 초정밀 스윙 분석기")
st.write("하나씩 순서대로 업로드하면 리소스 충돌을 피할 수 있습니다.")

# 1. 세션 상태 초기화 (영상이 날아가지 않게 보호)
if 'f_data' not in st.session_state:
    st.session_state.f_data = None
if 's_data' not in st.session_state:
    st.session_state.s_data = None

col1, col2 = st.columns(2)

with col1:
    st.subheader("📸 1. 정면 영상")
    f_input = st.file_uploader("정면 선택", type=['mp4', 'mov'], key="f_up")
    if f_input:
        st.session_state.f_data = f_input # 데이터 고정
    if st.session_state.f_data:
        st.video(st.session_state.f_data)
        st.success("✅ 정면 로드 완료")

with col2:
    st.subheader("📸 2. 측면 영상")
    s_input = st.file_uploader("측면 선택", type=['mp4', 'mov'], key="s_up")
    if s_input:
        st.session_state.s_data = s_input # 데이터 고정
    if st.session_state.s_data:
        st.video(st.session_state.s_data)
        st.success("✅ 측면 로드 완료")

# 2. 둘 다 완료되었을 때만 버튼 활성화
if st.session_state.f_data and st.session_state.s_data:
    st.divider()
    if st.button("📊 AI 스윙 분석 리포트 발행"):
        st.balloons()
        st.error("🚨 배치기(Early Extension) 주의!")
        st.info("💡 처방: 6월 아기 탄생 전까지 '의자 드릴'로 엉덩이 라인을 유지하세요.")
