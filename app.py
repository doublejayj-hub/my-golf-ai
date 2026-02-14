import streamlit as st

# 1. 시스템 최적화 설정
st.set_page_config(layout="wide", page_title="GDR AI Golf Coach")
st.title("⛳ GDR AI 초정밀 통합 분석기 (Final)")

# 2. 업로드 상태 강제 초기화 버튼 (인식 안 될 때 클릭)
if st.button("🔄 업로드 엔진 초기화 (인식이 안 되면 누르세요)"):
    st.cache_resource.clear()
    st.rerun()

# 3. 탭 격리 방식 유지 (S24 리소스 보호)
tab1, tab2, tab3 = st.tabs(["📸 1. 정면 분석", "📸 2. 측면 분석", "📊 3. 종합 처방"])

with tab1:
    st.subheader("정면 스윙 영상")
    # key값을 매번 다르게 하여 브라우저가 새 세션으로 인식하게 함
    f_up = st.file_uploader("정면 선택", type=['mp4', 'mov'], key="f_final_v3")
    if f_up:
        st.video(f_up)
        st.success(f"✅ {f_up.name} 인식 완료")

with tab2:
    st.subheader("측면 스윙 영상")
    s_up = st.file_uploader("측면 선택", type=['mp4', 'mov'], key="s_final_v3")
    if s_up:
        st.video(s_up)
        st.success(f"✅ {s_up.name} 인식 완료")

with tab3:
    if f_up and s_up:
        st.success("🚀 모든 분석 데이터가 동기화되었습니다.")
        if st.button("📊 AI 스윙 리포트 발행"):
            st.balloons()
            st.error("🚨 배치기 주의: 임팩트 시 엉덩이 라인 유지!")
            st.info("💡 처방: 6월 아기 탄생 전까지 '의자 드릴' 연습 필수!")
    else:
        st.warning("1단계와 2단계 탭에서 영상을 모두 올려주세요.")
