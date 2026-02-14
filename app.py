import streamlit as st

st.title("📡 서버 통신 테스트")

# 파일 업로드 시 즉시 화면에 이름을 띄우는 최소 로직
uploaded_file = st.file_uploader("파일을 선택해 보세요")

if uploaded_file is not None:
    st.write("### 🎉 성공! 파일이 서버에 도착했습니다.")
    st.write(f"파일명: {uploaded_file.name}")
    st.write(f"파일 크기: {uploaded_file.size} bytes")
else:
    st.info("파일을 선택했는데도 이 메시지가 안 바뀐다면 통신 차단 상태입니다.")
