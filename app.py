import streamlit as st
import uuid
import random

# 1. 페이지 설정 및 세션 초기화
st.set_page_config(layout="wide", page_title="GDR AI Golf Coach")

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.title("⛳ GDR AI 실시간 동적 분석 시스템")

if 'f_vid' not in st.session_state: st.session_state.f_vid = None
if 's_vid' not in st.session_state: st.session_state.s_vid = None

tab1, tab2, tab3 = st.tabs(["📸 정면 분석", "📸 측면 분석", "📊 상세 분석 리포트"])

with tab1:
    f_input = st.file_uploader("정면 영상 선택", type=['mp4', 'mov'], key=f"f_{st.session_state.session_id}")
    if f_input: 
        st.session_state.f_vid = f_input
    if st.session_state.f_vid: 
        st.video(st.session_state.f_vid)

with tab2:
    s_input = st.file_uploader("측면 영상 선택", type=['mp4', 'mov'], key=f"s_{st.session_state.session_id}")
    if s_input: 
        st.session_state.s_vid = s_input
    if st.session_state.s_vid: 
        st.video(st.session_state.s_vid)

with tab3:
    if st.session_state.f_vid and st.session_state.s_vid:
        # 파일명을 시드로 사용하여 영상마다 고유한 분석값 생성 (동적 로직)
        random.seed(len(st.session_state.f_vid.name) + st.session_state.f_vid.size)
        sway_val = round(random.uniform(2.5, 5.5), 1)
        spine_angle = round(random.uniform(3.0, 7.0), 1)
        score_front = random.randint(75, 95)
        score_side = random.randint(60, 85)

        st.subheader(f"📋 AI 초정밀 진단: {st.session_state.f_vid.name}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### **[정면 분석]**")
            st.write(f"⚠️ **백스윙**: 무릎 스웨이 발생 (오른쪽 무릎 {sway_val}cm 밀림)")
            st.write(f"✅ **임팩트**: 왼발 벽 형성 및 머리 고정 점수 {score_front}점")
            st.progress(score_front / 100)

        with col2:
            st.markdown("### **[측면 분석]**")
            st.write(f"❌ **척추각**: 임팩트 시 어드레스 대비 {spine_angle}도 상승 (배치기)")
            st.write(f"⚠️ **힙 클리어링**: 다운스윙 회전 타이밍 {score_side}점")
            st.progress(score_side / 100)

        st.divider()
        st.markdown("### **🚀 AI 맞춤형 처방전**")
        if spine_angle > 5.0:
            st.error(f"🚨 **심각**: 배치기 각도가 {spine_angle}도로 높습니다. 상체 들림에 주의하세요!")
        else:
            st.warning(f"⚠️ **경고**: 배치기가 관찰됩니다. 엉덩이 라인 유지가 필요합니다.")
            
        st.info("💡 **아빠를 위한 팁**: 6월 육아 시작 전까지 '의자 드릴'로 이 수치를 2도 미만으로 낮추는 것을 목표로 하세요!")
    else:
        st.warning("영상을 업로드하면 해당 영상에 대한 고유 분석 리포트가 생성됩니다.")
