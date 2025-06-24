import streamlit as st
import pandas as pd
from scipy.stats import chi2_contingency, chisquare

st.set_page_config(page_title="カイ二乗検定", layout="centered")
st.title("エクセルのクロス集計表に対するカイ二乗検定アプリ")

try:
    xls = pd.ExcelFile("cross.xlsx")
    sheet_names = xls.sheet_names
    sheet_name = st.selectbox("シートを選択してください", sheet_names)

    df = pd.read_excel(xls, sheet_name=sheet_name, index_col=0)
    with st.container():
        st.write("読み込まれたクロス集計表：")
        st.dataframe(df)

    test_type = st.radio("検定の種類を選んでください", ["独立性検定（行と列が独立か）", "適合度検定（観測が期待通りか）"])

    if test_type == "独立性検定（行と列が独立か）":
        st.subheader("▶ 独立性のカイ二乗検定")
        try:
            chi2, p, dof, expected = chi2_contingency(df)
            st.write(f"カイ二乗統計量: {chi2:.3f}")
            st.write(f"自由度: {dof}")
            st.write(f"p値: {p:.4f}")
            st.dataframe(pd.DataFrame(expected, index=df.index, columns=df.columns))

            if p < 0.05:
                st.success("帰無仮説（独立である）を棄却 → 行と列は有意に関係があります")
            else:
                st.info("帰無仮説（独立である）を採択 → 行と列は独立である可能性が高いです")
        except Exception as e:
            st.error(f"検定エラー: {e}")

    elif test_type == "適合度検定（観測が期待通りか）":
        st.subheader("▶ 適合度のカイ二乗検定")
        try:
            observed = df.sum(axis=1).values
            default_expected = ", ".join([str(round(x, 1)) for x in observed])
            expected_str = st.text_input("カンマ区切りで期待度数を入力してください", value=default_expected)

            if expected_str.strip():
                try:
                    expected_values = [float(x.strip()) for x in expected_str.split(",")]
                    if len(expected_values) != len(observed):
                        st.error("観測値と期待度数の長さが一致しません")
                    else:
                        chi2, p = chisquare(f_obs=observed, f_exp=expected_values)
                        st.write(f"観測値: {observed}")
                        st.write(f"期待値: {expected_values}")
                        st.write(f"カイ二乗統計量: {chi2:.3f}")
                        st.write(f"p値: {p:.4f}")
                        if p < 0.05:
                            st.success("帰無仮説（観測は期待通り）を棄却 → 観測値と期待値に差があります")
                        else:
                            st.info("帰無仮説（観測は期待通り）を採択 → 観測値は期待通りです")
                except ValueError:
                    st.error("期待度数の入力に誤りがあります。カンマ区切りの数値列を入力してください。")
        except Exception as e:
            st.error(f"検定エラー: {e}")
except FileNotFoundError:
    st.error("ファイル 'cross.xlsx' が見つかりません。アプリと同じディレクトリに配置してください。")
except Exception as e:
    st.error(f"Excel読み込みエラー: {e}")
