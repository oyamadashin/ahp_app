import streamlit as st
import numpy as np

# ページ設定
st.set_page_config(page_title="AHP_demo", layout = "wide")

# 画面を3分割
left, center, right = st.columns([1, 2, 1])


# セッションステートの初期化
if "page" not in st.session_state:
    st.session_state.page = "start"
if "criteria_matrix" not in st.session_state:
    st.session_state.criteria_matrix = None
if "weights" not in st.session_state:
    st.session_state.weights = None

# ページ遷移処理
def go_to(page_num):
    st.session_state.page = page_num
    st.rerun() # 強制的にスクリプト再実行（これをやらないと、その実行回でのpage_numのまま最後までスクリプトが実行されてしまう）

# スタート画面
def show_start():
    st.title("AHPで今日の晩ご飯を決めよう")
    st.markdown("AHPは、あなたが本当に求めているものを知るために役立つツールです")
    if st.button("はじめる"):
        go_to("criteria")

# 評価基準の一対比較画面
def show_criteria():
    with center:
        st.title("あなたは晩ご飯に何を求めますか？")
        st.write("どちらがより大事ですか？")
        st.write("安上がり vs おいしさ")
        # 一対比較スライダー
        criteria_choise2_score = st.slider("おいしさの優先度", 1/9, 9.0, 1.0, step=0.1)
        # 一対比較行列を保存
        st.session_state.criteria_matrix = np.array([
            [1, 1/criteria_choise2_score],
            [criteria_choise2_score, 1]
            ])
        # 一対比較行列を表示（確認用）
        st.write("評価基準の一対比較行列: ")
        st.dataframe(st.session_state.criteria_matrix)
    if st.button("次へ"):
        go_to("alternatives")

# 代替案の一対比較画面
def show_alternatives():
    st.title("晩ご飯を評価してください")
    # TODO 代替案の一対比較入力UI実装
    if st.button("次へ"):
        # TODO入力された比較を保存して重み付け計算
        go_to("result")


# 結果の表示画面
def show_result():
    st.title("これがあなたの今日の晩ご飯です")
    st.markdown("棒グラフが高いほど評価が高いことを意味します")
    # ウェイトを棒グラフで表示
    if st.button("はじめに戻る"):
        st.session_state.clear()
        go_to("start")

# ページの表示
if st.session_state.page == "start":
    show_start()
elif st.session_state.page == "criteria":
    show_criteria()
elif st.session_state.page == "alternatives":
    show_alternatives()
elif st.session_state.page == "result":
    show_result()
