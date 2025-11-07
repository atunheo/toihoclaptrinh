import streamlit as st
import gspread
from google.oauth2 import service_account
import datetime
import json

# ==============================
# ⚙️ CẤU HÌNH TRANG
# ==============================
st.set_page_config(page_title="Vòng Quay May Mắn", page_icon="🎡", layout="wide")

st.markdown("""
    <h1 style='text-align:center; color:#FFD700;'>
        🎡 Vòng Quay May Mắn (Google Sheets - Local Credential)
    </h1>
""", unsafe_allow_html=True)

# ==============================
# 🔐 KẾT NỐI GOOGLE SHEETS
# ==============================
SHEET_SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = "credentials.json"  # 👈 Đọc trực tiếp từ file

try:
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SHEET_SCOPE
    )
    client = gspread.authorize(creds)
except Exception as e:
    st.error(f"❌ Lỗi khi tải file credentials.json: {e}")
    st.stop()

# Lấy Google Sheet
try:
    sheets = client.openall()
    if not sheets:
        st.error("⚠️ Service account chưa có quyền truy cập Google Sheet nào. \
                 Hãy chia sẻ ít nhất 1 sheet với email trong file credentials.")
        st.stop()
    sheet = sheets[0].sheet1
    st.success(f"✅ Đang ghi vào sheet: **{sheet.title}**")
except Exception as e:
    st.error(f"❌ Lỗi khi kết nối Google Sheets: {e}")
    st.stop()

# ==============================
# 💫 HIỂN THỊ HTML + JS VÒNG QUAY
# ==============================
try:
    with open("a.html", "r", encoding="utf-8") as f:
        html = f.read()
except FileNotFoundError:
    st.error("❌ Không tìm thấy file `a.html`. Hãy đảm bảo file này nằm cùng thư mục với `a.py`.")
    st.stop()

st.components.v1.html(
    html + """
    <script>
        // Lắng nghe kết quả quay từ iframe HTML (JS gửi về)
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

# ==============================
# 🧾 GHI KẾT QUẢ VÀO GOOGLE SHEET
# ==============================
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
        st.error(f"❌ Lỗi khi ghi dữ liệu vào Google Sheet: {e}")
