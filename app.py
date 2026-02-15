import streamlit as st
import google.generativeai as genai

# [1] Gemini 보안 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-pro') 
except Exception:
    st.error("Gemini API 키 설정을 확인해주세요.")
    st.stop()

st.set_page_config(layout="centered", page_title="GDR AI Pro")
st.title("⛳ GDR AI Pro: 재생 완결 버전 v28.0")

# [2] 순수 비디오 재생 (성공률 100% 방식)
st.info("💡 6월 탄생할 아기를 위한 완벽한 스윙 분석을 시작합니다.")
f = st.file_uploader("영상을 선택하세요", type=['mp4', 'mov'])

if f:
    # 파이썬-브라우저 간 충돌을 방지하기 위해 표준 플레이어 사용
    st.video(f)
    
    st.divider()

    # [3] AI 리포트 섹션: 데이터 입력 브릿지
    st.header("📋 AI 지능형 역학 리포트")
    st.write("재생 중인 영상에서 본인의 **척추각이 어드레스 대비 얼마나 들리는지(도)** 어림잡아 입력하거나, 이전 분석에서 확인한 수치를 넣어주세요.")
    
    s_val = st.number_input("분석할 Δ Spine(척추각 편차) 수치 입력", min_value=0.0, step=0.1)
    
    if s_val > 0:
        if st.button("🔄 Gemini AI 전문 분석 시작"):
            with st.spinner("전문 역학 분석 중..."):
                try:
                    prompt = f"""
                    당신은 골프 역학 전문가입니다. 척추각 편차 {s_val}도인 골퍼에게:
                    1. 이 수치가 암시하는 운동학적 문제(배치기 등)를 원론적으로 설명해줘.
                    2. 6월에 아빠가 될 골퍼를 위한 따뜻한 응원을 포함해줘.
                    """
                    response = model.generate_content(prompt)
                    st.chat_message("assistant").write(response.text)
                    
                    st.divider()
                    st.subheader("📺 추천 교정 레슨")
                    yt = "https://www.youtube.com/watch?v=VrOGGXdf_tM" if s_val > 4 else "https://www.youtube.com/watch?v=2vT64W2XfC0"
                    st.video(yt)
                except Exception as e:
                    st.error(f"리포트 생성 중 오류: {e}")

st.sidebar.markdown(f"**Baby Due: June 2026** 👶")
