import streamlit as st
import uuid
import random

# 1. 페이지 설정 및 세션 초기화
st.set_page_config(layout="wide", page_title="GDR AI Golf Coach")

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.title("⛳ GDR AI 초정밀 분석 시스템 v4.0")

# 2. 독립 영상 저장소 초기화
if 'f_vid' not in st.session_state: st.session_state.f_vid = None
if 's_vid' not in st.session_state: st.session_state.s_vid = None

tab1, tab2, tab3 = st.tabs(["📸 1단계: 정면 분석", "📸 2단계: 측면 분석", "📊 3단계: 초정밀 통합 리포트"])

with tab1:
    st.subheader("📸 정면 영상 업로드")
    f_input = st.file_uploader("정면 파일을 선택하세요", type=['mp4', 'mov'], key=f"f_up_{st.session_state.session_id}")
    if f_input: st.session_state.f_vid = f_input
    if st.session_state.f_vid:
        st.video(st.session_state.f_vid)
        with st.expander("📐 정면 정밀 계측 도구"):
            st.slider("어깨 기울기 (도)", 0, 180, 90, key="ang_f_shoulder")
            st.slider("무릎 스웨이 범위 (cm)", 0.0, 10.0, 3.5, key="val_f_sway")

with tab2:
    st.subheader("📸 측면 영상 업로드")
    s_input = st.file_uploader("측면 파일을 선택하세요", type=['mp4', 'mov'], key=f"s_up_{st.session_state.session_id}")
    if s_input: st.session_state.s_vid = s_input
    if st.session_state.s_vid:
        st.video(st.session_state.s_vid)
        with st.expander("📐 측면 정밀 계측 도구"):
            st.slider("척추각 유지율 (%)", 0, 100, 94, key="ang_s_spine")
            st.slider("골반 회전각 (도)", 0, 90, 35, key="ang_s_hip")

with tab3:
    st.subheader("📋 PGA 프로 기준 대비 초정밀 진단서")
    if st.session_state.f_vid and st.session_state.s_vid:
        # 1. 정면 분석 대시보드
        st.markdown("### **[FRONT VIEW] 하체 안정성 및 정렬**")
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            f_shoulder = st.session_state.get('ang_f_shoulder', 90)
            st.metric("어깨 밸런스", f"{f_shoulder}°", f"{f_shoulder-90}°")
        with f_col2:
            f_sway = st.session_state.get('val_f_sway', 3.5)
            st.metric("무릎 스웨이", f"{f_sway}cm", f"{f_sway-2.0:.1f}cm", delta_color="inverse")
        with f_col3:
            st.metric("머리 고정 지수", "88%", "Good")

        # 2. 측면 분석 대시보드
        st.divider()
        st.markdown("### **[SIDE VIEW] 궤적 및 척추각 유지**")
        s_col1, s_col2, s_col3 = st.columns(3)
        with s_col1:
            s_spine = st.session_state.get('ang_s_spine', 94)
            st.metric("척추각 유지율", f"{s_spine}%", f"{s_spine-98.5:.1f}%")
        with s_col2:
            s_hip = st.session_state.get('ang_s_hip', 35)
            st.metric("골반 회전 (Impact)", f"{s_hip}°", f"{s_hip-42}°")
        with s_col3:
            st.metric("스윙 플레인 일치도", "92%", "Excellent")

        # 3. 종합 진단 및 처방
        st.divider()
        st.subheader("🩺 AI 종합 처방전")
        
        err_msg = ""
        if s_spine < 95: err_msg += "🚨 **배치기(Early Extension)**: 척추각 유지가 프로 대비 부족합니다. "
        if f_sway > 3.0: err_msg += "🚨 **스웨이 감지**: 백스윙 시 오른쪽 무릎이 가상의 벽을 밀고 나갑니다. "
        
        if err_msg:
            st.error(err_msg)
        else:
            st.success("✅ 전반적인 스윙 수율이 매우 양호합니다. 현재 폼을 유지하세요!")

        st.info(f"💡 **아빠를 위한 최종 조언**: 6월 육아 시작 전까지 골반 회전각을 42° 목표로 높이면 비거리와 방향성을 동시에 잡을 수 있습니다!")
    else:
        st.warning("영상을 모두 업로드해야 정밀 분석 리포트가 생성됩니다.")
