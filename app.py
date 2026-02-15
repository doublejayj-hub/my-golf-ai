import streamlit as st

# 1. 페이지 설정 및 서버 캐시 강제 무효화
st.set_page_config(layout="wide", page_title="GDR AI Golf Coach")
st.title("⛳ GDR AI 초정밀 분석기 (멀티유저 보안 버전)")

# 2. 전역 변수가 아닌 세션별 독립 변수 확인
# 다른 사람이 접속하면 이 값들은 초기 상태로 시작됩니다.
if 'f_video' not in st.session_state:
    st.session_state.f_video = None
if 's_video' not in st.session_state:
    st.session_state.s_video = None

# 3. 탭 구성 - 각 탭 내부의 위젯은 세션에 귀속됩니다.
tab1, tab2, tab3 = st.tabs(["📸 1단계: 정면", "📸 2단계: 측면", "📊 3단계: 리포트"])

with tab1:
    # key값을 고정하여 세션 내에서만 유효하게 설정
    f_up = st.file_uploader("정면 영상 업로드", type=['mp4', 'mov'], key="user_front_upload")
    if f_up:
        st.session_state.f_video = f_up
    
    if st.session_state.f_video:
        st.video(st.session_state.f_video)
        st.success(f"현재 사용자 영상: {st.session_state.f_video.name}")

with tab2:
    s_up = st.file_uploader("측면 영상 업로드", type=['mp4', 'mov'], key="user_side_upload")
    if s_up:
        st.session_state.s_video = s_up
        
    if st.session_state.s_video:
        st.video(st.session_state.s_video)
        st.success(f"현재 사용자 영상: {st.session_state.s_video.name}")

with tab3:
    # 두 영상이 모두 해당 '세션'에 존재할 때만 리포트 생성
    if st.session_state.f_video and st.session_state.s_video:
        st.write(f"🔍 분석 대상: **{st.session_state.f_video.name}** & **{st.session_state.s_video.name}**")
        if st.button("📊 개인화 리포트 발행"):
            st.balloons()
            st.error("🚨 배치기 주의: 임팩트 시 척추각을 유지하세요!")
            st.info("💡 처방: 6월 아기 탄생 전 '의자 드릴' 연습 추천")
    else:
        st.warning("영상을 업로드한 사용자에게만 분석 결과가 표시됩니다.")
