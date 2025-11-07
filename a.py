import streamlit as st
import requests
import datetime
import json

# ⚙️ Cấu hình trang
st.set_page_config(page_title="Vòng Quay May Mắn", page_icon="🎡", layout="wide")

st.markdown("""
    <h1 style='text-align:center; color:#FFD700;'>
        🎡 Vòng Quay May Mắn (Google Sheets qua Apps Script)
    </h1>
""", unsafe_allow_html=True)

# 🧩 Thay bằng URL Web App bạn vừa deploy
API_URL = "https://script.google.com/macros/s/AKfycbx72N-OAU5ABpu9CF7sZMEZd3L4ypafwYJm1yOU-Cls0zYV3bxixqmbAGY0f9Wrwyk/exec"

# ==== HIỂN THỊ HTML + JS ====
with open("a.html", "r", encoding="utf-8") as f:
    html = f.read()

st.components.v1.html(
    html + f"""
    <script>
        window.addEventListener("message", (event) => {{
            if (event.data && event.data.type === "SPIN_RESULT") {{
                const prize = event.data.prize;
                const now = new Date().toLocaleString("vi-VN");
                const payload = {{time: now, prize: prize}};
                fetch("{API_URL}", {{
                    method: "POST",
                    headers: {{ "Content-Type": "application/json" }},
                    body: JSON.stringify(payload)
                }})
                .then(r => r.json())
                .then(resp => console.log("Đã gửi:", resp))
                .catch(err => console.error("Lỗi:", err));
            }}
        }});
    </script>
    """,
    height=850,
    scrolling=True,
)
