import streamlit as st
import random
import math
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Vòng Quay May Mắn", page_icon="🎡", layout="centered")

# ===== Khởi tạo session state =====
if "prizes" not in st.session_state:
    st.session_state.prizes = []
if "history" not in st.session_state:
    st.session_state.history = []

st.title("🎡 Vòng Quay May Mắn")

# ===== Quản lý phần thưởng =====
with st.expander("🎁 Quản lý phần thưởng"):
    with st.form("add_prize_form"):
        name = st.text_input("Tên phần thưởng")
        quantity = st.number_input("Số lượng", min_value=1, value=1)
        weight = st.number_input("Tỷ lệ (Trọng số)", min_value=1, value=1)
        color = st.color_picker("Màu sắc", "#3b82f6")
        submitted = st.form_submit_button("Thêm")

        if submitted and name:
            st.session_state.prizes.append({
                "name": name,
                "originalQuantity": quantity,
                "quantity": quantity,
                "weight": weight,
                "color": color
            })

    if st.session_state.prizes:
        df = pd.DataFrame(st.session_state.prizes)
        st.dataframe(df)
        remove = st.text_input("Nhập tên phần thưởng cần xóa:")
        if st.button("Xóa"):
            st.session_state.prizes = [p for p in st.session_state.prizes if p["name"] != remove]
            st.success("Đã xóa!")

# ===== Quay vòng =====
if st.session_state.prizes:
    if st.button("🎯 QUAY"):
        # Lọc phần thưởng còn hàng
        available = [p for p in st.session_state.prizes if p["quantity"] > 0]
        if not available:
            st.warning("Đã hết phần thưởng!")
        else:
            # Weighted random
            weighted = []
            for p in available:
                weighted += [p] * p["weight"]
            prize = random.choice(weighted)

            # Trừ số lượng
            for p in st.session_state.prizes:
                if p["name"] == prize["name"]:
                    p["quantity"] -= 1

            # Lưu lịch sử
            st.session_state.history.append({
                "time": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M:%S"),
                "prize": prize["name"]
            })

            st.success(f"🎉 Chúc mừng! Bạn trúng **{prize['name']}**!")

else:
    st.info("Hãy thêm phần thưởng trước khi quay.")

# ===== Lịch sử quay =====
st.subheader("📜 Lịch sử quay")
if st.session_state.history:
    df_hist = pd.DataFrame(st.session_state.history)
    st.dataframe(df_hist)

    buffer = BytesIO()
    df_hist.to_excel(buffer, index=False)
    st.download_button(
        label="📥 Tải Excel",
        data=buffer.getvalue(),
        file_name="lich_su_quay_thuong.xlsx",
        mime="application/vnd.ms-excel"
    )

# ===== Reset =====
st.divider()
col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Reset lịch sử"):
        st.session_state.history = []
        for p in st.session_state.prizes:
            p["quantity"] = p["originalQuantity"]
        st.success("Đã reset lịch sử quay.")
with col2:
    if st.button("🧨 Reset toàn bộ"):
        st.session_state.clear()
        st.success("Đã xóa toàn bộ dữ liệu.")
