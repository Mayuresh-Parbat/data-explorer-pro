import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Data Explorer Pro+", layout="wide")

st.title("🚀 Data Explorer Pro+")

menu = st.sidebar.selectbox("Navigation", [
    "Overview",
    "Filter Data",
    "Visualization",
    "Insights"
])

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # ================= OVERVIEW =================
    if menu == "Overview":
        st.markdown("## 📌 Dataset Overview")
        st.markdown("---")

        # ===== METRICS =====
        col1, col2, col3 = st.columns(3)
        col1.metric("Rows", df.shape[0])
        col2.metric("Columns", df.shape[1])
        col3.metric("Missing Values", df.isnull().sum().sum())

        # ===== DATA QUALITY SCORE =====
        st.markdown("### 📊 Data Quality Score")

        missing = df.isnull().sum().sum()
        duplicates = df.duplicated().sum()

        score = 100
        score -= min(30, missing * 0.1)
        score -= min(30, duplicates * 0.5)

        st.progress(int(score))
        st.success(f"Data Quality Score: {int(score)}/100")

        # ===== QUICK INSIGHTS =====
        st.markdown("### ⚡ Quick Insights")

        colA, colB, colC = st.columns(3)

        num_cols = df.select_dtypes(include=np.number).columns
        cat_cols = df.select_dtypes(include="object").columns

        if len(num_cols) > 0:
            colA.metric("Avg Value", round(df[num_cols[0]].mean(), 2))

        if len(cat_cols) > 0:
            top = df[cat_cols[0]].value_counts().idxmax()
            colB.metric("Top Category", top)

        colC.metric("Unique Columns", df.nunique().mean())

        # ===== EXPLAIN DATA =====
        st.markdown("### 🧠 Explain My Data")

        if st.button("Analyze Dataset"):
            insights = []

            insights.append(f"Dataset has {df.shape[0]} rows and {df.shape[1]} columns.")

            if missing > 0:
                insights.append(f"Contains {missing} missing values.")

            if len(cat_cols) > 0:
                col = cat_cols[0]
                top = df[col].value_counts().idxmax()
                insights.append(f"'{col}' is dominated by '{top}'.")

            if len(num_cols) > 0:
                col = num_cols[0]
                insights.append(f"'{col}' average is {round(df[col].mean(),2)}.")

            for i in insights:
                st.success(i)

        # ===== DATA PREVIEW =====
        st.markdown("### 📄 Data Preview")
        st.dataframe(df, use_container_width=True)

    # ================= FILTER =================
    elif menu == "Filter Data":
        st.markdown("## 🔍 Filter Data")
        st.markdown("---")

        column = st.selectbox("Select column", df.columns)

        if df[column].dtype == "object":
            value = st.selectbox("Value", df[column].unique())
            filtered_df = df[df[column] == value]
        else:
            min_val = float(df[column].min())
            max_val = float(df[column].max())
            value = st.slider("Range", min_val, max_val, (min_val, max_val))
            filtered_df = df[(df[column] >= value[0]) & (df[column] <= value[1])]

        st.dataframe(filtered_df, use_container_width=True)

        csv = filtered_df.to_csv(index=False).encode()
        st.download_button("Download CSV", csv, "filtered.csv")

    # ================= VISUALIZATION =================
    elif menu == "Visualization":
        st.markdown("## 📊 Visualization")
        st.markdown("---")

        numeric_cols = df.select_dtypes(include=np.number).columns
        cat_cols = df.select_dtypes(include="object").columns

        # ===== SMART SUGGESTION =====
        if len(cat_cols) > 0:
            st.info(f"💡 Suggested: Bar chart for '{cat_cols[0]}'")

        chart_type = st.selectbox("Chart", ["Bar", "Line", "Histogram"])

        if chart_type == "Histogram":
            col = st.selectbox("Numeric Column", numeric_cols)
            st.bar_chart(df[col].value_counts())

        elif chart_type == "Line":
            col = st.selectbox("Numeric Column", numeric_cols)
            st.line_chart(df[col])

        else:
            col = st.selectbox("Category Column", cat_cols)
            st.bar_chart(df[col].value_counts().head(10))

        # ===== DATE TREND =====
        st.markdown("### 📅 Trend Analysis")

        for c in df.columns:
            try:
                df[c] = pd.to_datetime(df[c])
                st.line_chart(df[c].value_counts().sort_index())
                break
            except:
                continue

    # ================= INSIGHTS =================
    elif menu == "Insights":
        st.markdown("## 🔥 Insights")
        st.markdown("---")

        st.markdown("### Missing Values")
        st.bar_chart(df.isnull().sum())

        st.markdown("### Outliers")

        num_cols = df.select_dtypes(include=np.number).columns

        for col in num_cols:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            outliers = df[(df[col] < (q1 - 1.5 * iqr)) | (df[col] > (q3 + 1.5 * iqr))]
            st.write(f"{col}: {len(outliers)} outliers")

else:
    st.info("📂 Upload a CSV file to start.")