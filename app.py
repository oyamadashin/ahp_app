import streamlit as st

# ページ設定
st.set_page_config(page_title="AHP_demo", layout = "wide")

# 画面を3分割
left, center, right = st.columns([1, 2, 1])

with center:
    st.title("AHPで今日の晩ご飯を決めよう")