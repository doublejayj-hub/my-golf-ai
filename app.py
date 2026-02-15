import streamlit as st
import uuid
import random

# 1. 페이지 설정
st.set_page_config(layout="wide", page_title="GDR AI Golf Coach")

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.title("⛳ GDR AI 초정밀 분석기: 수동 계측 & 프로 비교")

# 2. 프로 표준 데이터셋
PRO_STANDARDS = {"spine": 98.5, "hip": 42.0, "head": 1.5}

if 'f_vid' not in st.session_state: st.session_state.f_vid = None
if 's_vid' not in st.session_state: st.session_state.s_vid = None

tab1, tab2, tab3 = st.tabs(["📸 영상 분석 & 수동 계측", "📊 Pro-Standard 비교", "📋 분석 가이드"])

# 분석 도구 렌더링 함수
def render_analysis_tool(video_file, side_name):
    if video_file:
        st.video(video_file)
        with st.expander(f"📐 {side_name} 수동 각도기 및 드로잉 도구"):
            st.write("S24 화면에서 영상을 멈추고 슬라이더를 조절하세요.")
            col_a, col_b = st.columns(2)
            with col_a:
                st.slider(f"{side_name} 측정 각도 (도)", 0, 180, 90, key=f"ang_{side_name}")
            with col_b:
                st.slider(f"{side_name} 가이드라인 위치", 0, 100, 50, key=f"pos_{side_name}")

# 메인 실행부
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        f_in = st.file_uploader("정면 선택", type=['mp4', 'mov'], key=f"f_{st.session_state.session_id}")
        if f_in: 
            st.session_state.f_vid = f_in
        if st.session_state.f_vid:
            render_analysis_tool(st.session_state.f_vid, "정면")
            
    with col2:
        s_in = st.file_uploader("측면 선택", type=['mp4', 'mov'], key=f"s_{st.session_state.session_id}")
        if s_in: 
            st.session_state.s_vid = s_in
        if st.session_state.s_vid:
            render_analysis_tool(st.session_state.s_vid, "측면")

with tab2:
    if st.session_state.f_vid and st.session_state.s_vid:
        st.subheader("📋 프로 데이터 대비 수율 분석")
        random.seed(st.session_state.session_id)
        
        # 슬라이더에서 측정값 가져오기 (없으면 기본값 92)
        my_spine = st.session_state.get('ang_측면', 92)
        delta = round(my_spine - PRO_STANDARDS['spine'], 1)
        
        c1, c2 = st.columns(2)
        with c1:
            st.metric("수동 측정 척추각 유지율", f"{my_spine}%", f"{delta}%", delta_color="normal")
        with c2:
            st.metric("프로 표준 척추각", f"{PRO_STANDARDS['spine']}%")
        
        st.divider()
        st.error(f"🚨 **종합 진단**: 배치기 위험군. 6월 육아 시작 전까지 교정이 필요합니다!")
    else:
        st.warning("영상을 업로드하면 분석 도구가 활성화됩니다.")

with tab3:
    st.markdown("### 📖 초정밀 계측 가이드")
    st.write("1. 영상을 멈추고 2. 수동 각도기 슬라이더를 조절하여 3. 프로 수치와 비교하세요.")
