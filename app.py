import streamlit as st
import uuid
import random

# 1. 페이지 설정
st.set_page_config(layout="wide", page_title="GDR AI Golf Coach")

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.title("⛳ GDR AI 초정밀 분석기: 터치 계측 & 프로 비교")

# 2. 프로 표준 데이터셋 (고정)
PRO_STANDARDS = {"spine": 98.5, "hip": 42.0, "head": 1.5}

if 'f_vid' not in st.session_state: st.session_state.f_vid = None
if 's_vid' not in st.session_state: st.session_state.s_vid = None

tab1, tab2, tab3 = st.tabs(["📸 영상 분석 & 수동 계측", "📊 Pro-Standard 비교", "📋 분석 가이드"])

# 분석 로직 함수 (반복 사용)
def render_analysis_tool(video_file, side_name):
    if video_file:
        st.video(video_file)
        # 2번 기능: 반자동 계측 도구 UI
        with st.expander(f"📐 {side_name} 수동 각도기 및 드로잉 도구 활성화"):
            st.write("S24 화면에서 영상을 멈추고 아래 슬라이더로 가이드라인을 맞춰보세요.")
            col_a, col_b = st.columns(2)
            with col_a:
                angle = st.slider(f"{side_name} 측정 각도 (도)", 0, 180, 90, key=f"ang_{side_name}")
                st.write(f"현재 측정값: **{angle}°**")
            with col_b:
                line_pos = st.slider(f"{side_name} 가이드라인 위치", 0, 100, 50, key=f"pos_{side_name}")
                st.write(f"가이드라인 오프셋: **{line_pos}%**")
            st.info(f"💡 {side_name}의 핵심 관절(어깨/척추)에 슬라이더를 맞춰 실제 각도를 기록하세요.")

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        f_in = st.file_uploader("정면 선택", type=['mp4', 'mov'], key=f"f_{st.session_state.session_id}")
        if f_in: st.session_state.f_vid = f_in
        render_analysis_tool(st.session_state.f_vid, "정면")
    with c2:
        s_in = st.file_uploader("측면 선택", type=['mp4', 'mov'], key=f"s_{st.session_state.session_id}")
        if s_in: st.session_state.s_vid = s_in
        render_analysis_tool(st.session_state.s_vid, "측면")

with tab2:
    if st.session_state.f_vid and st.session_state.s_vid:
        st.subheader("📋 프로 데이터 대비 수율 분석")
        random.seed(st.session_state.session_id)
        
        # 수동 계측값을 반영한 리포트 (슬라이더 값 연동 가능)
        my_spine = st.session_state.get('ang_측면', 92)
        
        col1, col2 = st.columns(2)
        with col1:
