import streamlit as st
import uuid

# 1. 페이지 설정 및 세션 ID 생성
st.set_page_config(layout="wide", page_title="GDR AI Golf Coach")

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.title("⛳ GDR AI 초정밀 분석기 (문법 및 탭 격리 완벽 수정본)")

# 2. 독립 영상 저장소 초기화
if 'f_vid' not in st.session_state: st.session_state.f_vid = None
if 's_vid' not in st.session_state: st.session_state.s_vid = None

# 3. 탭 분리 구성 (S24 리소스 및 세션 보호)
tab1, tab2, tab3 = st.tabs(["📸 1단계: 정면 분석", "📸 2단계: 측면 분석", "📊 3단계: 통합 리포트"])

with tab1:
    st.subheader("📸 정면 영상 업로드")
    f_input = st.file_uploader("정면 파일을 선택하세요", type=['mp4', 'mov'], key=f"f_up_{st.session_state.session_id}")
    if f_input:
        st.session_state.f_vid = f_input
    
    if st.session_state.f_vid:
        st.video(st.session_state.f_vid)
        with st.expander("📐 정면 수동 계측 (어깨/무릎)"):
            st.slider("어깨 수평도 체크", 0, 180, 90, key="ang_f_tool")

with tab2:
    st.subheader("📸 측면 영상 업로드")
    s_input = st.file_uploader("측면 파일을 선택하세요", type=['mp4', 'mov'], key=f"s_up_{st.session_state.session_id}")
    if s_input:
        st.session_state.s_vid = s_input
        
    if st.session_state.s_vid:
        st.video(st.session_state.s_vid)
        with st.expander("📐 측면 수동 계측 (척추/배치기)"):
            st.slider("척추각 유지율 (%)", 0, 100, 95, key="ang_s_tool")

with tab3:
    st.subheader("📋 종합 분석 및 프로 대비 수율")
    if st.session_state.f_vid and st.session_state.s_vid:
        st.success("🚀 데이터 분석 준비 완료!")
        
        # 계측 데이터 시각화
        f_val = st.session_state.get('ang_f_tool', 90)
        s_val = st.session_state.get('ang_s_tool', 95)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("정면 어깨 밸런스", f"{f_val}°", f"{f_val-90}°")
        with col2:
            st.metric("측면 척추 유지율", f"{s_val}%", f"{s_val-98.5:.1f}%")
        
        st.divider()
