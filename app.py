import streamlit as st
import uuid
import random

# 1. 페이지 설정 및 사용자 세션 ID 생성
st.set_page_config(layout="wide", page_title="GDR AI Golf Coach")

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.title("⛳ GDR AI 초정밀 분석기 (탭 격리 및 계측 통합)")

# 2. 세션별 독립 영상 저장소 초기화
if 'f_vid' not in st.session_state: st.session_state.f_vid = None
if 's_vid' not in st.session_state: st.session_state.s_vid = None

# 3. 탭 분리 구성 (S24 리소스 최적화 전략)
tab1, tab2, tab3 = st.tabs(["📸 1단계: 정면 분석", "📸 2단계: 측면 분석", "📊 3단계: 통합 리포트"])

with tab1:
    st.subheader("정면 영상 분석")
    f_input = st.file_uploader("정면 영상 선택", type=['mp4', 'mov'], key=f"f_{st.session_state.session_id}")
    if f_input:
        st.session_state.f_vid = f_input
    
    if st.session_state.f_vid:
        st.video(st.session_state.f_vid)
        with st.expander("📐 정면 수동 계측 도구 (어깨/무릎)"):
            st.slider("어깨 수평 각도", 0, 180, 90, key="ang_front")
            st.info("💡 어드레스 시 어깨 라인에 맞춰 수평도를 체크하세요.")

with tab2:
    st.subheader("측면 영상 분석")
    s_input = st.file_uploader("측면 영상 선택", type=['mp4', 'mov'], key=f"s_{st.session_state.session_id}")
    if s_input:
        st.session_state.s_vid = s_input
        
    if st.session_state.s_vid:
        st.video(st.session_state.s_vid)
        with st.expander("📐 측면 수동 계측 도구 (척추/배치기)"):
            st.slider("척추각 유지도 (%)", 0, 100, 95, key="ang_side")
            st.info("💡 임팩트 시 척추각이 얼마나 유지되는지 슬라이더로 기록하세요.")

with tab3:
    if st.session_state.f_vid and st.session_state.s_vid:
        st.success("🚀 양방향 데이터 분석 준비 완료!")
        
        # 프로 기준 데이터 대비 분석 리포트
        f_val = st.session_state.get('ang_front', 90)
        s_val = st.session_state.get('ang_side', 95)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("정면 어깨 수평", f"{f_val}°", f"{f_val-90}°")
        with col2:
            st.metric("측면 척추 유지", f"{s_val}%", f"{s_val-98.5:.1f}%")
        
        st.divider()
        st.markdown("### **🎯 AI 맞춤형 처방**")
        if s_val < 95:
            st.error("🚨 **배치기 경고**: 척추각 유지가 프로 대비 부족합니다.")
        
        st.info("💡 **아빠를 위한 조언**: 6
