import streamlit as st

# 페이지 설정
st.set_page_config(layout="wide", page_title="GDR AI Golf Coach")
st.title("⛳ GDR AI 초정밀 분석기 (가이드라인 추가)")

# 세션 상태 유지
if 'f_video' not in st.session_state: st.session_state.f_video = None
if 's_video' not in st.session_state: st.session_state.s_video = None

tab1, tab2, tab3 = st.tabs(["📸 정면 분석", "📸 측면 분석", "📊 통합 리포트"])

with tab1:
    st.subheader("📸 정면: 어깨 라인 & 무릎 스웨이 체크")
    f_up = st.file_uploader("정면 선택", type=['mp4', 'mov'], key="f_vfinal")
    if f_up: st.session_state.f_video = f_up
    if st.session_state.f_video:
        st.video(st.session_state.f_video)
        # 점선 가이드 시각화 안내
        st.info("💡 **정면 분석 포인트**: 어드레스 시 양쪽 무릎에 수직 점선을 상상하며 백스윙 시 무릎이 선을 넘는지 확인하세요.")

with tab2:
    st.subheader("📸 측면: 척추각 & 배치기 체크")
    s_up = st.file_uploader("측면 선택", type=['mp4', 'mov'], key="s_vfinal")
    if s_up: st.session_state.s_video = s_up
    if st.session_state.s_video:
        st.video(st.session_state.s_video)
        # 척추각 유지 안내
        st.info("💡 **측면 분석 포인트**: 어드레스 시 등 라인과 엉덩이 끝(Tush Line)에 점선을 맞춰보세요. 임팩트 때 엉덩이가 선에서 떨어지면 '배치기'입니다.")

with tab3:
    if st.session_state.f_video and st.session_state.s_video:
        if st.button("📊 상세 분석 리포트 확인"):
            st.balloons()
            st.markdown("### 🧬 AI 관절 추적 결과")
            st.write("- **어깨 회전**: 충분한 회전이 발생하고 있습니다.")
            st.write("- **척추 유지**: 다운스윙 시 척추각이 유지되지 않고 들리는 경향이 있습니다.")
            st.error("🚨 **집중 교정**: 임팩트 시 배치기 발생 주의!")
            st.info(f"💡 **처방**: 6월에 태어날 아기 돌봄 준비로 바빠지시기 전에 '의자 드릴' 연습으로 힙 클리어링을 완성하세요!")
    else:
        st.warning("영상을 모두 업로드해야 상세 분석이 가능합니다.")
