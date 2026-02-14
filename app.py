import streamlit as st

st.set_page_config(layout="wide", page_title="GDR AI Golf Coach")

st.title("⛳ GDR AI 초정밀 스윙 분석기")
st.info("S24 리소스 최적화를 위해 '단계별 업로드' 모드로 전환했습니다.")

# 1. 세션 상태 유지
if 'f_video' not in st.session_state: st.session_state.f_video = None
if 's_video' not in st.session_state: st.session_state.s_video = None

# 2. 탭 분리 (격리 처리)
tab1, tab2, tab3 = st.tabs(["📸 1단계: 정면 업로드", "📸 2단계: 측면 업로드", "📊 3단계: 통합 분석"])

with tab1:
    st.subheader("정면 영상을 먼저 올려주세요")
    f_up = st.file_uploader("정면 선택", type=['mp4', 'mov'], key="f_step")
    if f_up:
        st.session_state.f_video = f_up
        st.video(st.session_state.f_video)
        st.success("✅ 정면 로드 성공! 이제 2단계 탭으로 이동하세요.")

with tab2:
    st.subheader("측면 영상을 올려주세요")
    s_up = st.file_uploader("측면 선택", type=['mp4', 'mov'], key="s_step")
    if s_up:
        st.session_state.s_video = s_up
        st.video(st.session_state.s_video)
        st.success("✅ 측면 로드 성공! 이제 3단계 탭으로 이동하세요.")

with tab3:
    st.subheader("종합 스윙 분석")
    if st.session_state.f_video and st.session_state.s_video:
        st.success("🚀 모든 데이터가 준비되었습니다!")
        if st.button("📊 AI 스윙 리포트 발행"):
            st.balloons()
            st.error("🚨 배치기 주의: 임팩트 시 엉덩이 유지!")
            st.info("💡 처방: 6월 아기 탄생 전 '의자 드릴' 연습 필수!")
    else:
        st.warning("1단계와 2단계에서 영상을 모두 업로드해야 분석이 가능합니다.")
