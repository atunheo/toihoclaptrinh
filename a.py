import streamlit as st
import random
import math
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Vòng Quay May Mắn", page_icon="🎡", layout="centered")

# ===== Khởi tạo session state =====
if "prizes" not in st.session_state:
    st.session_state.prizes = []
if "history" not in st.session_state:
    st.session_state.history = []
if "rotation" not in st.session_state:
    st.session_state.rotation = 0  # Góc quay hiện tại (rad)

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

# ===== Hàm vẽ vòng quay =====
def draw_wheel(prizes, rotation=0):
    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw={'projection': 'polar'})
    ax.set_theta_direction(-1)
    ax.set_theta_offset(math.pi / 2.0)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_facecolor("#111")

    if not prizes:
        ax.text(0.5, 0.5, "Chưa có phần thưởng", ha='center', va='center', color='white', fontsize=16, transform=ax.transAxes)
        return fig

    total = len(prizes)
    arc = 2 * math.pi / total

    for i, prize in enumerate(prizes):
        start = i * arc + rotation
        end = start + arc
        ax.bar(
            x=start + arc / 2,
            height=1,
            width=arc,
            color=prize["color"],
            edgecolor="white",
            linewidth=2,
            align="center"
        )
        ax.text(start + arc / 2, 0.7, prize["name"], color="white", ha="center", va="center", rotation=0, fontsize=10)

    # Con trỏ ở trên
    ax.plot([math.pi / 2, math.pi / 2], [0, 1.05], color="red", linewidth=4)
    return fig

# ===== Hiển thị vòng quay =====
st.subheader("🌀 Vòng quay")
fig = draw_wheel(st.session_state.prizes, st.session_state.rotation)
st.pyplot(fig)

# ===== Quay vòng =====
if st.session_state.prizes:
    if st.button("🎯 QUAY"):
        available = [p for p in st.session_state.prizes if p["quantity"] > 0]
        if not available:
            st.warning("Đã hết phần thưởng!")
        else:
            # Weighted random
            weighted = []
            for p in available:
                weighted += [p] * p["weight"]
            prize = random.choice(weighted)

            # Giảm số lượng
            for p in st.session_state.prizes:
                if p["name"] == prize["name"]:
                    p["quantity"] -= 1

            # Lưu lịch sử
            st.session_state.history.append({
                "time": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M:%S"),
                "prize": prize["name"]
            })

            # Cập nhật góc quay (random 5–10 vòng)
            idx = st.session_state.prizes.index(prize)
            total = len(st.session_state.prizes)
            arc = 2 * math.pi / total
            random_offset = random.uniform(0.1, 0.9) * arc
            target_angle = idx * arc + random_offset
            total_spin = random.randint(5, 10) * 2 * math.pi
            st.session_state.rotation += total_spin - target_angle  # để trỏ vào phần thưởng

            st.success(f"🎉 Chúc mừng! Bạn trúng **{prize['name']}**!")

            # Vẽ lại vòng quay sau khi quay
            fig = draw_wheel(st.session_state.prizes, st.session_state.rotation)
            st.pyplot(fig)
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
