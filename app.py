import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="GDR AI Golf Coach")

st.title("⛳ GDR AI 초정밀 스윙 분석기")

with st.sidebar:
    st.header("📽️ 영상 업로드")
    f_file = st.file_uploader("정면 영상 (GDR)", type=['mp4', 'mov'], key="front")
    s_file = st.file_uploader("측면 영상 (GDR)", type=['mp4', 'mov'], key="side")

# 파일이 하나만 올라와도 상태를 표시하도록 수정
if f_file or s_file:
    if f_file:
        st.write(f"✅ 정면 영상 로드 완료: {f_file.name}")
    if s_file:
        st.write(f"✅ 측면 영상 로드 완료: {s_file.name}")
    
    if f_file and s_file:
        st.success("🚀 모든 영상이 준비되었습니다. 아래 분석 창을 확인하세요.")
        # 브라우저 엔진 호출
        components.html("<h3>🖥️ 브라우저 분석 모듈 가동 중...</h3>", height=100)
else:
    st.warning("왼쪽 사이드바에서 파일을 선택해 주세요. 용량이 클 경우 잠시 기다려야 할 수 있습니다.")
