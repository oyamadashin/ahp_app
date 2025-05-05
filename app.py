import streamlit as st
import numpy as np
import pandas as pd

# ページ設定
st.set_page_config(page_title="AHP_demo", layout="wide")

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
if "theme" not in st.session_state:
    st.session_state.theme = "今日の晩ご飯"
if "criterion1" not in st.session_state:
    st.session_state.criterion1 = "おいしさ"
if "criterion2" not in st.session_state:
    st.session_state.criterion2 = "安上がり"
if "alternative1" not in st.session_state:
    st.session_state.alternative1 = "カレー"
if "alternative2" not in st.session_state:
    st.session_state.alternative2 = "野菜炒め"
if "alternative3" not in st.session_state:
    st.session_state.alternative3 = "すき焼き"


# ページ遷移処理
def go_to(page_num):
    st.session_state.page = page_num
    st.rerun()  # 強制的にスクリプト再実行（これをやらないと、その実行回でのpage_numのまま最後までスクリプトが実行されてしまう）


# 行列からウェイトを求める関数
def geometric_mean_weights(matrix):
    product = np.prod(matrix, axis=1)  # 行方向に各要素を乗じた値を求める
    geo_mean = product ** (1 / matrix.shape[0])  # 幾何平均を求める
    return geo_mean / np.sum(geo_mean)  # ウェイトを求める


# スタート画面
def show_start():
    with center:
        st.title("AHPで〇〇〇〇を決めよう")
        st.markdown(
            """
            - 人はたくさんのものを同時に比べるのは苦手ですが、2つのものを比べるのは得意です。このような**一対比較**を活かして最適な選択肢を決める手法が**AHP**です。
            - このAHP体験デモでは、**スライダー**を動かして、一対比較を何回かくりかえすことで、あなたにとって最適な今日の晩ご飯を決めることができます。
            """
        )
        st.image("static/images/slider.jpg")  # スライダー操作を解説する画像
        col1, col2 = st.columns(2)
        with col1:
            if st.button("初めての人はこちら"):
                go_to("criteria")
        with col2:
            if st.button("慣れた人はこちら"):
                go_to("input")


# TODO 評価基準と選択肢を入力させる画面
def show_input():
    with center:
        st.session_state.theme = st.text_input(
            "決めたいことを教えてください", value="今日の晩ご飯"
        )
        st.session_state.criterion1 = st.text_input(
            "評価基準1を入力してください",
            value="おいしさ",
        )
        st.session_state.criterion2 = st.text_input(
            "評価基準2を入力してください",
            value="安上がり",
        )
        st.session_state.alternative1 = st.text_input(
            "選択肢1を入力してください", value="カレー"
        )
        st.session_state.alternative2 = st.text_input(
            "選択肢2を入力してください",
            value="野菜炒め",
        )
        st.session_state.alternative3 = st.text_input(
            "選択肢3を入力してください",
            value="すき焼き",
        )

        if st.button("次へ"):
            go_to("criteria")


# 評価基準の一対比較画面
def show_criteria():
    with center:
        st.title("Q-0")
        st.markdown(
            f"""
            <div style="text-align: center;">
                {st.session_state.theme}を決めるにあたり、次のどちらを重視しますか？<br>
                <b>{st.session_state.criterion1}</b> vs <b>{st.session_state.criterion2}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with center:
        # 一対比較スライダー
        log_criteria_score = st.slider(
            label="",
            min_value=-1.0,  # 表示する値は-1, 1
            max_value=1.0,
            value=0.0,
            step=0.1,
            key=f"slider_criteria",
        )
        st.image("static/images/axis_label.jpg", use_column_width=True)
        # st.markdown(
        #     """
        #     <div style ="text-align: center;">
        #         ← こちらの方が重要　　　　　同程度　　　　　こちらの方が重要 →
        #     </div>
        #     """,
        #     unsafe_allow_html=True,
        # )

    # -1～1のスケールにしていたlog(1/9)～log(9)にした上で、指数変換して「差」を「比」に戻す
    criteria_score = np.exp(log_criteria_score * np.log(9))
    # 一対比較行列を保存
    st.session_state.criteria_matrix = np.array(
        [[1, criteria_score], [1 / criteria_score, 1]]
    )

    with center:
        if st.button("次へ"):
            go_to("alternatives")


# 代替案の一対比較画面
def show_alternatives():
    with center:
        st.markdown(
            f"# Q-{st.session_state.criteria_index+1}-{st.session_state.comparison_step+1}"
        )
    # 代替案
    alternatives = [
        st.session_state.alternative1,
        st.session_state.alternative2,
        st.session_state.alternative3,
    ]
    criteria = [st.session_state.criterion2, st.session_state.criterion1]
    # 代替案の一対比較ペアの番号(行列に格納するときに使う)
    pairs = [(0, 1), (0, 2), (1, 2)]

    # 現在のステップと基準インデックス
    step = st.session_state.comparison_step
    crit_idx = st.session_state.criteria_index

    # 比較する代替案のインデックス
    i, j = pairs[step]
    a1, a2 = alternatives[i], alternatives[j]

    with center:
        st.markdown(
            f"""
            **「{criteria[crit_idx]}」** という評価基準において、どちらを高く評価しますか？
            """
        )

        st.markdown(
            f"""
            <div style="text-align: center;">
                <b>{a2}</b> vs <b>{a1}</b>  
            </div>
            """,
            unsafe_allow_html=True,
        )

        # スライダーで入力(対数スケールで)
        log_score = st.slider(
            label="",
            min_value=-1.0,  # ユーザーに表示する値は-1, 1
            max_value=1.0,
            value=0.0,
            step=0.1,
            key=f"slider_{crit_idx}_{step}",
        )
        st.image("static/images/axis_label.jpg", use_column_width=True)
        # st.markdown(
        #     """
        #     <div style ="text-align: center;">
        #         ← こちらの方を高く評価する　　　　　同程度　　　　　こちらの方を高く評価する →
        #     </div>
        #     """,
        #     unsafe_allow_html=True,
        # )
    # -1～1にしていたスケールをlog(1/9)～log(9)にした上で、指数変換で「差」を「比」に変換
    ratio = np.exp(log_score * np.log(9))

    st.session_state.weights[crit_idx][i, j] = ratio
    st.session_state.weights[crit_idx][j, i] = 1 / ratio

    with center:
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
    with center:
        st.markdown(
            f"""
                # これがあなたの望む{st.session_state.theme}です
            """
        )

    # 一対比較表の対角要素を1にする
    for mat in st.session_state.weights:
        np.fill_diagonal(mat, 1)

    # 評価基準のウェイトを求める
    criteria_weights = geometric_mean_weights(st.session_state.criteria_matrix)

    # 代替案のウェイトを求める
    alt_weights = [geometric_mean_weights(mat) for mat in st.session_state.weights]

    # 総合評価を求める
    final_weights = np.array(alt_weights).T @ criteria_weights

    with center:
        import matplotlib.pyplot as plt
        import matplotlib as mpl
        from matplotlib import font_manager

        # フォントファイルのパスを指定(renderはLinuxベースなので、msゴシック等を指定すると文字化けしてしまう)
        font_path = "fonts/ipaexg.ttf"
        font_prop = font_manager.FontProperties(fname=font_path)
        plt.rcParams["font.family"] = font_prop.get_name()

        alternatives = [
            st.session_state.alternative1,
            st.session_state.alternative2,
            st.session_state.alternative3,
        ]
        fig, ax = plt.subplots(figsize=(1.0, 1.0))
        wedges, texts, autotexts = ax.pie(
            final_weights,
            labels=alternatives,  # 凡例に使うラベル
            autopct="%1.1f%%",  # パーセンテージ表示
            startangle=90,  # 見栄えのためにスタート角度を調整
            textprops={"fontproperties": font_prop},
        )
        # 割合（内側の文字）のフォントサイズ変更（必要なら）
        for autotext in autotexts:
            autotext.set_fontsize(6)
        ax.axis("equal")  # 円形にするための設定
        st.pyplot(fig)
        st.markdown(
            f"""
            割合が大きいほど、あなたにとって望ましい{st.session_state.theme}であることを意味します。
            """
        )

        if st.button("はじめに戻る"):
            st.session_state.clear()
            go_to("start")


# ページの表示
if st.session_state.page == "start":
    show_start()
elif st.session_state.page == "input":
    show_input()
elif st.session_state.page == "criteria":
    show_criteria()
elif st.session_state.page == "alternatives":
    show_alternatives()
elif st.session_state.page == "result":
    show_result()
