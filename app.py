import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(
    page_title="SaSaC V2 預測系統",
    page_icon="🌭",
    layout="centered"
)

st.title("🌭 SaSaC 香腸補貨預測系統")
st.markdown("支援品項：黑豬肉、竹筍、高粱、米腸。請上傳含日期與銷售資料的 CSV 檔案。")

uploaded_file = st.file_uploader("📂 上傳你的 CSV 檔案", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        try:
            df = pd.read_csv(uploaded_file, encoding='big5')
        except:
            df = pd.read_csv(uploaded_file, encoding='cp950')

    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date')

    item_options = ['黑豬肉', '竹筍', '高粱', '米腸']
    selected_item = st.selectbox("🍢 選擇預測品項", item_options)

    if selected_item in df.columns and '是否下雨' in df.columns:
        df['移動平均'] = df[selected_item].rolling(window=3).mean()

        st.subheader("🌦️ 預測條件")
        is_rain_next = st.radio("下次是否預測為下雨天？", ["否", "是"]) == "是"
        adjustment = st.slider("📉 額外手動修正（±%）", -50, 50, 0)
        factor = 1 + adjustment / 100

        latest_ma = df['移動平均'].dropna().iloc[-1]
        predicted = latest_ma * (0.8 if is_rain_next else 1.0) * factor
        st.success(f"建議補貨：**{round(predicted)} 支 {selected_item}**")

        st.subheader("📈 銷售趨勢圖")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df['date'], df[selected_item], label='實際銷售', marker='o')
        ax.plot(df['date'], df['移動平均'], label='3次移動平均', linestyle='--')
        for i, row in df.iterrows():
            if row['是否下雨'] == True:
                ax.annotate('☔', (row['date'], row[selected_item] + 2), fontsize=10, ha='center', color='blue')
        ax.set_title(f"{selected_item} 銷售趨勢")
        ax.set_xlabel("日期")
        ax.set_ylabel("銷售量（支）")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

        if st.checkbox("📋 顯示原始資料"):
            st.dataframe(df[['date', selected_item, '是否下雨', '移動平均']])
    else:
        st.error("❌ 請確認資料中包含指定品項與『是否下雨』欄位")
