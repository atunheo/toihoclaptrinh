import streamlit as st
import gspread
from google.oauth2 import service_account
import datetime
import json

st.set_page_config(page_title="Vòng Quay May Mắn", page_icon="🎡", layout="wide")

st.markdown("""
    <h1 style='text-align:center; color:#FFD700;'>
        🎡 Vòng Quay May Mắn (Google Linked)
    </h1>
""", unsafe_allow_html=True)

# ==== Kết nối Google Sheets ====
SHEET_ID = "1FSRN3RIT5mqt1oQc57VOdqqaWzi0_A6fOwDSAavKwpI"  # 👈 thay bằng ID thật
SHEET_SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]

# ⚠️ Dùng st.secrets thay vì file credentials.json
creds = service_account.Credentials.from_service_account_info(
    st.secrets["google"],  # lấy từ Streamlit Secrets
    scopes=SHEET_SCOPE
)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

# ==== Component HTML + JS ====
with open("a.html", "r", encoding="utf-8") as f:
    html = f.read()

st.components.v1.html(
    html + """
    <script>
        // Lắng nghe thông điệp từ iframe HTML (JS gửi về)
        window.addEventListener("message", (event) => {
            if (event.data && event.data.type === "SPIN_RESULT") {
                const prize = event.data.prize;
                const now = new Date().toLocaleString("vi-VN");
                const payload = {time: now, prize: prize};
                fetch(window.location.href, {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify(payload)
                });
            }
        });
    </script>
    """,
    height=850,
    scrolling=True,
)

# ==== Xử lý dữ liệu POST (khi JS gửi kết quả) ====
from streamlit.runtime.scriptrunner import get_script_run_ctx

ctx = get_script_run_ctx()
if ctx and hasattr(ctx, "request_body") and ctx.request_body:
    try:
        data = json.loads(ctx.request_body)
        prize_name = data.get("prize", "Không rõ")
        time_str = data.get("time", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        sheet.append_row([time_str, prize_name])
        st.toast(f"🎉 Đã lưu kết quả: {prize_name}")
    except Exception as e:
        st.error(f"Lỗi khi ghi dữ liệu: {e}")
