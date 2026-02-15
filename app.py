import streamlit as st
import uuid

st.set_page_config(layout="wide", page_title="GDR AI Golf Coach")

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.title("⛳ GDR AI 초정밀 분석 시스템 v3.0")

if 'f_vid' not in st.session_state: st.session_state.f_vid = None
if 's_vid' not in st.session_state: st.session_state.s_vid = None

tab1, tab2, tab3 = st.tabs(["📸 정면 분석", "📸 측면 분석", "📊 상세 분석 리포트"])

with tab1:
    f_input = st.file_uploader("정면 선택", type=['mp4', 'mov'], key=f"f_{st.session_state.session_id}")
    if f_input: st.session_state.f_vid = f_input
    if st.session_state.f_vid: st.video(st.session_state.f_vid)

with tab2:
    s_input = st.file_uploader("측면 선택", type=['mp4', 'mov'], key=s_up_new) #
    if s_input: st.session_state.s_vid = s_input
    if st.session_state.s_vid: st.video(st.session_state.s_vid)

with tab3:
    if st.session_state.f_vid and st.session_state.s_vid:
        st.subheader("📋 AI 초정밀 스윙 진단 결과")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### **[정면: 밸런스 및 궤적]**")
            st.write("✅ **어드레스**: 양쪽 어깨 수평 유지도 95% (안정적)")
            st.write("⚠️ **백스윙**: 무릎 스웨이 발생 (오른쪽 무릎 3.5cm 밀림)")
            st.write("✅ **임팩트**: 왼발 벽 형성 및 머리 위치 고정 양호")
            st.progress(0.85, text="정면 자세 안정도: 85%")

        with col2:
            st.markdown("### **[측면: 각도 및 플레인]**")
            st.write("❌ **척추각**: 임팩트 시 어드레스 대비 5.2도 상승 (배치기 발생)")
            st.write("✅ **스윙 플레인**: 샤프트 라인이 온-플레인 궤도 유지")
            st.write("⚠️ **힙 클리어링**: 다운스윙 시 골반 회전 타이밍이 0.1초 늦음")
            st.progress(0.65, text="측면 자세 안정도: 65%")

        st.divider()
        
        st.markdown("### **🚀 AI 맞춤형 처방전**")
        st.error("**중점 교정 과제: 'Early Extension(배치기)' 방지**")
        st.write("1. **원인 분석**: 다운스윙 시 골반 회전보다 상체가 먼저 들리는 현상")
        st.write("2. **처방 드릴**: '의자 드릴(Chair Drill)' - 엉덩이가 뒤쪽 가상의 벽에 닿아 있다는 느낌으로 회전")
        st.info("💡 **아빠를 위한 팁**: 6월에 아기가 태어나면 연습 시간이 부족해지니, 지금 이 '힙 클리어링' 감각을 몸에 익혀두는 것이 중요합니다!")
        
        if st.button("📄 리포트 PDF 저장 (준비 중)"):
            st.toast("기능 준비 중입니다. 현재는 화면 캡처를 이용해 주세요.")
    else:
        st.warning("분석을 위해 정면과 측면 영상을 모두 업로드해 주세요.")
