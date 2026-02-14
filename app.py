import streamlit as st

st.set_page_config(page_title="Network Test")
st.title("📡 서버 통신 최종 점검")

# 업로드 상태를 확인하기 위한 가장 단순한 구성
file = st.file_uploader("S24에서 파일을 선택해 보세요")

if file:
    st.balloons()
    st.success(f"성공! 파일이 서버에 닿았습니다: {file.name}")
else:
    st.warning("파일을 선택했는데도 이 글자가 안 바뀐다면 네트워크 차단 상태입니다.")
