import streamlit as st
import gspread
from google.oauth2 import service_account
import datetime
import json

st.set_page_config(page_title="Vòng Quay May Mắn", page_icon="🎡", layout="wide")

st.markdown("""
    <h1 style='text-align:center; color:#FFD700;'>
        🎡 Vòng Quay May Mắn (Streamlit Cloud)
    </h1>
""", unsafe_allow_html=True)

# ==== Kết nối Google Sheets qua st.secrets ====
SHEET_SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]

creds = service_account.Credentials.from_service_account_info(
    st.secrets["google"], scopes=SHEET_SCOPE
)
client = gspread.authorize(creds)

# Lấy sheet đầu tiên
sheets = client.openall()
if not sheets:
    st.error("⚠️ Không tìm thấy Google Sheet nào mà service account có quyền.\n\n➡️ Hãy chia sẻ ít nhất 1 sheet với email trong service account.")
    st.stop()

sheet = sheets[0].sheet1
st.success(f"✅ Đang ghi vào sheet: **{sheet.title}**")

# ==== HTML + JS vòng quay ====
with open("a.html", "r", encoding="utf-8") as f:
    html = f.read()

st.components.v1.html(
    html + """
    <script>
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

# ==== Ghi kết quả vào Sheet ====
from streamlit.runtime.scriptrunner import get_script_run_ctx

ctx = get_script_run_ctx()
if ctx and hasattr(ctx, "request_body") and ctx.request_body:
    try:
        data = json.loads(ctx.request_body)
        prize = data.get("prize", "Không rõ")
        time_str = data.get("time", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        sheet.append_row([time_str, prize])
        st.toast(f"🎉 Đã lưu kết quả: {prize}")
    except Exception as e:
        st.error(f"❌ Lỗi khi ghi dữ liệu: {e}")
