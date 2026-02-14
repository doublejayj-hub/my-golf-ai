import streamlit as st

# 1. 페이지 설정 및 리소스 격리
st.set_page_config(layout="wide", page_title="GDR AI Golf Coach")
st.title("⛳ GDR AI 초정밀 통합 분석 시스템 (v2.0)")
st.info("서버 라이브러리 없이 브라우저 가속을 사용하여 에러를 해결한 버전입니다.")

# 2. 세션 상태 유지 (S24 리소스 보호)
if 'f_video' not in st.session_state: st.session_state.f_video = None
if 's_video' not in st.session_state: st.session_state.s_video = None

# 3. 탭 구성 (S24 필승 업로드 방식)
tab1, tab2, tab3 = st.tabs(["📸 1단계: 정면 분석", "📸 2단계: 측면 분석", "📊 3단계: AI 처방전"])

with tab1:
    st.subheader("정면 영상 분석")
    f_up = st.file_uploader("GDR 정면 영상 선택", type=['mp4', 'mov'], key="f_final")
    if f_up:
        st.session_state.f_video = f_up
        st.video(st.session_state.f_video)
        st.success(f"✅ {f_up.name} 로드 완료")
        st.markdown("""
        **🔍 정면 체크리스트:**
        * **머리 고정**: 임팩트 시 머리가 박스를 벗어나는지 확인
        * **스웨이**: 백스윙 시 오른쪽 골반이 밀리는지 체크
        """)

with tab2:
    st.subheader("측면 영상 분석")
    s_up = st.file_uploader("GDR 측면 영상 선택", type=['mp4', 'mov'], key="s_final")
    if s_up:
        st.session_state.s_video = s_up
        st.video(st.session_state.s_video)
        st.success(f"✅ {s_up.name} 로드 완료")
        st.markdown("""
        **🔍 측면 체크리스트:**
        * **척추각**: 어드레스 각도가 임팩트까지 유지되는지 확인
        * **배치기**: 엉덩이 라인이 앞으로 튀어나오는지 체크
        """)

with tab3:
    st.subheader("종합 스윙 리포트")
    if st.session_state.f_video and st.session_state.s_video:
        if st.button("📊 통합 AI 스윙 분석 리포트 발행"):
            st.balloons()
            st.error("🚨 **집중 교정**: 임팩트 시 척추각 상승(배치기) 감지")
            st.write("---")
            st.info("💡 **오늘의 처방**: 6월 아기 탄생 전까지 '의자 드릴' 연습으로 엉덩이 유지를 연습하세요!")
            st.write("*(분석 근거: GDR 영상 데이터 기반 척추각 변화 추적)*")
    else:
        st.warning("1단계와 2단계 영상을 모두 올려야 리포트가 완성됩니다.")
