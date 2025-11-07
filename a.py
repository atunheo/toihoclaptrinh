import streamlit as st

st.set_page_config(page_title="Vòng Quay May Mắn", page_icon="🎡", layout="wide")

st.markdown(
    """
    <h1 style='text-align: center; color: #FFD700;'>
        🎡 Vòng Quay May Mắn 
    </h1>
    """,
    unsafe_allow_html=True
)

# Đọc nội dung file HTML
with open("a.html", "r", encoding="utf-8") as f:
    html_code = f.read()

# Nhúng HTML vào Streamlit
st.components.v1.html(html_code, height=800, scrolling=True)
