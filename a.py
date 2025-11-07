import streamlit as st
import gspread
from google.oauth2 import service_account
import datetime
import json

# ==============================
# 🎡 CẤU HÌNH TRANG
# ==============================
st.set_page_config(page_title="Vòng Quay May Mắn", page_icon="🎡", layout="wide")

st.markdown("""
    <h1 style='text-align:center; color:#FFD700;'>
        🎡 Vòng Quay May Mắn (Google Linked)
    </h1>
""", unsafe_allow_html=True)

# ==============================
# 🔐 KẾT NỐI GOOGLE SHEETS
# ==============================
# Đường dẫn đến file credentials.json của bạn
SERVICE_ACCOUNT_FILE = "credentials.json"  # 👈 đặt file này trong cùng thư mục với a.py

# Scope cho phép đọc + ghi dữ liệu vào Google Sheets
SHEET_SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]

# Đọc credentials từ file JSON
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SHEET_SCOPE
)
client = gspread.authorize(creds)

# 👉 Lấy danh sách tất cả các Google Sheets mà service account có quyền
sheets_list = client.openall()

if not sheets_list:
    st.error("❌ Không tìm thấy file Google Sheet nào mà service account có quyền truy cập.\n\n➡️ Hãy chia sẻ Google Sheet với email trong service account (ví dụ: dinhuy@vongquay-may.iam.gserviceaccount.com)")
    st.stop()

# Lấy sheet đầu tiên (hoặc thay bằng tên cụ thể nếu bạn muốn)
sheet = sheets_list[0].sheet1
SHEET_ID = sheet.spreadsheet.id

st.info(f"📄 Đang kết nối với Google Sheet: **{sheet.title}** (ID: `{SHEET_ID}`)")

# ==============================
# 💫 HIỂN THỊ HTML + JS VÒNG QUAY
# ==============================
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

# ==============================
# 🧾 NHẬN DỮ LIỆU POST TỪ JS & LƯU VÀO SHEET
# ==============================
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
