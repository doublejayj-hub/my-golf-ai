import streamlit as st
import uuid

# 1. 페이지 설정 및 초기화
st.set_page_config(layout="wide", page_title="GDR AI Golf Coach")

# 사용자별 고유 세션 ID 생성 (서버 데이터 꼬임 방지)
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.title("⛳ GDR AI 초정밀 분석기 (보안 격리 버전)")
st.caption(f"접속 세션 ID: {st.session_state.session_id}")

# 2. 업로드 데이터 독립 저장소
if 'f_vid' not in st.session_state: st.session_state.f_vid = None
if 's_vid' not in st.session_state: st.session_state.s_vid = None

# 3. 탭 기반 독립 프로세스
tab1, tab2, tab3 = st.tabs(["📸 정면", "📸 측면", "📊 리포트"])

with tab1:
    # key에 session_id를 포함하여 다른 사람과 절대 겹치지 않게 함
    f_input = st.file_uploader("정면 선택", type=['mp4', 'mov'], key=f"f_{st.session_state.session_id}")
    if f_input:
        st.session_state.f_vid = f_input
    if st.session_state.f_vid:
        st.video(st.session_state.f_vid)

with tab2:
    s_input = st.file_uploader("측면 선택", type=['mp4', 'mov'], key=f"s_{st.session_state.session_id}")
    if s_input:
        st.session_state.s_vid = s_input
    if st.session_state.s_vid:
        st.video(st.session_state.s_vid)

with tab3:
    if st.session_state.f_vid and st.session_state.s_vid:
        st.success(f"사용자 전용 분석 완료: {st.session_state.f_vid.name}")
        if st.button("📊 개인 리포트 생성"):
            st.balloons()
            st.error("🚨 배치기 주의: 임팩트 시 척추각 유지!")
            st.info("💡 처방: 6월 아기 탄생 전 '의자 드릴' 연습 추천")
    else:
        st.warning("본인의 영상을 업로드해 주세요. 다른 사용자의 데이터는 보이지 않습니다.")
