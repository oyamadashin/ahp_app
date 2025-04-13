import streamlit as st
import numpy as np
import pandas as pd

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
    st.session_state.weights = [np.zeros((3, 3)) for _ in range(2)]
if "comparison_step" not in st.session_state:
    st.session_state.comparison_step = 0
if "criteria_index" not in st.session_state:
    st.session_state.criteria_index = 0

# ページ遷移処理
def go_to(page_num):
    st.session_state.page = page_num
    st.rerun() # 強制的にスクリプト再実行（これをやらないと、その実行回でのpage_numのまま最後までスクリプトが実行されてしまう）

# 行列からウェイトを求める関数
def geometric_mean_weights(matrix):
    product = np.prod(matrix, axis = 1) # 行方向に各要素を乗じた値を求める
    geo_mean = product ** (1 / matrix.shape[0]) # 幾何平均を求める
    return geo_mean / np.sum(geo_mean) # ウェイトを求める


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
        
    # 左右ラベル付きスライダー（HTMLで実現）
    st.markdown("""
    <div style="display: flex; justify-content: space-between; padding: 0 1.5em;">
        <span>安上がり</span>
        <span>おいしさ</span>
    </div>
    """, unsafe_allow_html=True)

    with center:
        # スライダーでは「比」を「差」として示すため、対数を使う
        min_log_value = np.log(1/9)
        max_log_value = np.log(9)
        # 一対比較スライダー
        log_criteria_choise2_score = st.slider(
            label = "",
            min_value= min_log_value, 
            max_value = max_log_value, 
            value = 0.0, 
            step=0.1,
            key = f"slider_criteria")
        
    # 指数変換して「差」を「比」に戻す
    criteria_choise2_score = np.exp(log_criteria_choise2_score)
    # 一対比較行列を保存
    st.session_state.criteria_matrix = np.array([
        [1, 1/criteria_choise2_score],
        [criteria_choise2_score, 1]
        ])

    # デバッグ用
    with center:
        st.dataframe(st.session_state.criteria_matrix)

    if st.button("次へ"):
        go_to("alternatives")


# 代替案の一対比較画面
def show_alternatives():
    st.title("晩ご飯を評価してください")
    # 代替案
    alternatives = ["カレー", "野菜炒め", "すき焼き"]
    criteria = ["安上がり", "おいしさ"]
    # 代替案の一対比較ペアの番号(行列に格納するときに使う)
    pairs = [(0, 1), (0, 2), (1, 2)]


    # 現在のステップと基準インデックス
    step = st.session_state.comparison_step
    crit_idx = st.session_state.criteria_index

    # 比較する代替案のインデックス
    i, j = pairs[step]
    a1, a2 = alternatives[i], alternatives[j]

    st.write(f"「{criteria[crit_idx]}かどうか」という評価基準において、どちらが重要ですか？")
    st.write(f"{a1} vs {a2}")
    
    # スライダーで入力(対数スケールで)
    log_score = st.slider(
        label= "", 
        min_value= np.log(1/9), 
        max_value=np.log(9), 
        value=0.0, 
        step = 0.1,
        key = f"slider_{crit_idx}_{step}")
    # 指数変換で「差」を「比」に変換
    ratio = np.exp(log_score)

    st.session_state.weights[crit_idx][i, j] = ratio
    st.session_state.weights[crit_idx][j, i] = 1 / ratio

    if st.button("次へ"):
        st.session_state.comparison_step += 1
        if st.session_state.comparison_step >= len(pairs):
            st.session_state.comparison_step = 0
            st.session_state.criteria_index += 1

            if st.session_state.criteria_index >= len(criteria):
                go_to("result")
            else:
                st.rerun()
        else:
            st.rerun()


# 結果の表示画面
def show_result():
    st.title("これがあなたの今日の晩ご飯です")

    # 一対比較表の対角要素を1にする
    for mat in st.session_state.weights:
        np.fill_diagonal(mat, 1)

    # 評価基準のウェイトを求める
    criteria_weights = geometric_mean_weights(st.session_state.criteria_matrix)

    # 代替案のウェイトを求める
    alt_weights = [geometric_mean_weights(mat) for mat in st.session_state.weights]

    # 総合評価を求める
    final_weights = np.array(alt_weights).T @ criteria_weights

    st.markdown("棒グラフが高いほど評価が高いことを意味します")
    # デバッグ用
    alternatives = ["カレー", "野菜炒め", "すき焼き"]
    df = pd.DataFrame([final_weights], columns=alternatives, index=["総合評価"])
    with center:
        st.dataframe(df)   
    # TODO ウェイトを棒グラフで表示
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
