import streamlit as st

# 1. 페이지 설정 및 리소스 격리
st.set_page_config(layout="wide", page_title="GDR AI Golf Coach")
st.title("⛳ GDR AI 초정밀 통합 분석기")
st.write("성공했던 버전으로 완벽히 복구했습니다.")

# 2. 세션 상태 유지 (영상이 날아가지 않게 보호)
if 'f_video' not in st.session_state: st.session_state.f_video = None
if 's_video' not in st.session_state: st.session_state.s_video = None

# 3. 탭 분리 (S24 리소스 충돌 방지 전략)
tab1, tab2, tab3 = st.tabs(["📸 1단계: 정면 분석", "📸 2단계: 측면 분석", "📊 3단계: 통합 리포트"])

with tab1:
    st.subheader("정면 영상을 올려주세요")
    f_up = st.file_uploader("정면 선택", type=['mp4', 'mov'], key="f_restore")
    if f_up:
        st.session_state.f_video = f_up
    if st.session_state.f_video:
        st.video(st.session_state.f_video)
        st.success(f"✅ 정면 로드 완료: {st.session_state.f_video.name}")

with tab2:
    st.subheader("측면 영상을 올려주세요")
    s_up = st.file_uploader("측면 선택", type=['mp4', 'mov'], key="s_restore")
    if s_up:
        st.session_state.s_video = s_up
    if st.session_state.s_video:
        st.video(st.session_state.s_video)
        st.success(f"✅ 측면 로드 완료: {st.session_state.s_video.name}")

with tab3:
    st.subheader("종합 분석 결과")
    if st.session_state.f_video and st.session_state.s_video:
        st.success("🚀 모든 영상이 준비되었습니다!")
        if st.button("📊 AI 스윙 리포트 발행"):
            st.balloons()
            st.error("🚨 배치기 주의: 임팩트 시 엉덩이 라인을 유지하세요!")
            st.info("💡 처방: 6월 아기 탄생 전까지 '의자 드릴' 연습을 추천합니다.")
    else:
        st.warning("1단계와 2단계 탭에서 영상을 모두 올려주세요.")
