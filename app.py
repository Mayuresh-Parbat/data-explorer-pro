import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Data Explorer Pro", layout="wide")

st.title("📊 Data Explorer Pro")

# ===== SIDEBAR =====
menu = st.sidebar.selectbox("Navigation", [
    "Overview",
    "Filter Data",
    "Visualization",
    "Insights"
])

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # ===== OVERVIEW =====
    if menu == "Overview":
        st.markdown("## 📌 Dataset Overview")
        st.markdown("---")

        col1, col2, col3 = st.columns(3)
        col1.metric("Rows", df.shape[0])
        col2.metric("Columns", df.shape[1])
        col3.metric("Missing Values", df.isnull().sum().sum())

        st.markdown("")

        st.markdown("### 📄 Data Preview")
        st.dataframe(df, use_container_width=True)

        st.markdown("### 📊 Column Information")
        col_info = pd.DataFrame({
            "Column": df.columns,
            "Data Type": df.dtypes,
            "Missing Values": df.isnull().sum()
        })
        st.dataframe(col_info, use_container_width=True)

        st.markdown("### 📌 Data Types Distribution")
        st.write(df.dtypes.value_counts())

    # ===== FILTER DATA =====
    elif menu == "Filter Data":
        st.markdown("## 🔍 Filter Data")
        st.markdown("---")

        column = st.selectbox("Select column", df.columns)

        if df[column].dtype == "object":
            value = st.selectbox("Select value", df[column].unique())
            filtered_df = df[df[column] == value]
        else:
            min_val = float(df[column].min())
            max_val = float(df[column].max())
            value = st.slider("Select range", min_val, max_val, (min_val, max_val))
            filtered_df = df[(df[column] >= value[0]) & (df[column] <= value[1])]

        st.markdown("### 📄 Filtered Data")
        st.dataframe(filtered_df, use_container_width=True)

        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇ Download Filtered Data", csv, "filtered_data.csv", "text/csv")

    # ===== VISUALIZATION =====
    elif menu == "Visualization":
        st.markdown("## 📊 Data Visualization")
        st.markdown("---")

        # Suggest better columns
        good_cols = [col for col in df.columns if df[col].nunique() < 50]

        if good_cols:
            st.info(f"💡 Suggested columns for charts: {good_cols[:5]}")

        col1, col2 = st.columns([1, 2])

        with col1:
            chart_type = st.selectbox("Chart Type", ["Bar", "Line", "Histogram"])

        with col2:
            chart_col = st.selectbox("Select Column", df.columns)

        st.markdown("")

        # Avoid bad charts
        if df[chart_col].nunique() > 50 and df[chart_col].dtype == "object":
            st.warning("⚠ This column has too many unique values (like IDs). Choose another column.")
        else:
            st.markdown("### 📈 Chart Output")

            if chart_type == "Bar":
                if df[chart_col].dtype == "object":
                    st.bar_chart(df[chart_col].value_counts().head(10))
                else:
                    st.bar_chart(df[chart_col])

            elif chart_type == "Line":
                if df[chart_col].dtype != "object":
                    st.line_chart(df[chart_col])
                else:
                    st.warning("Line chart works better with numeric data.")

            elif chart_type == "Histogram":
                if df[chart_col].dtype != "object":
                    st.bar_chart(df[chart_col].value_counts().sort_index())
                else:
                    st.warning("Histogram requires numeric data.")

        st.markdown("---")

        # Compare columns
        st.markdown("### 🔗 Compare Two Numeric Columns")

        num_cols = df.select_dtypes(include=np.number).columns.tolist()

        if len(num_cols) >= 2:
            colA, colB = st.columns(2)

            with colA:
                x_col = st.selectbox("X-axis", num_cols)

            with colB:
                y_col = st.selectbox("Y-axis", num_cols)

            st.line_chart(df[[x_col, y_col]])
        else:
            st.warning("⚠ No sufficient numeric columns found for comparison. Try another dataset.")

        st.markdown("---")

        # Correlation
        st.markdown("### 🔥 Correlation Matrix")

        num_df = df.select_dtypes(include=np.number)

        if not num_df.empty:
            st.dataframe(num_df.corr(), use_container_width=True)
        else:
            st.warning("⚠ No numeric columns available for correlation analysis.")

    # ===== INSIGHTS =====
    elif menu == "Insights":
        st.markdown("## 🔥 Key Insights")
        st.markdown("---")

        column = st.selectbox("Select column for insights", df.columns)

        st.markdown("### 📊 Top Values")
        st.write(df[column].value_counts().head(5))

        st.markdown("### ⚠ Missing Values")
        st.bar_chart(df.isnull().sum())

        st.markdown("### ⚠ Outlier Detection")

        num_cols = df.select_dtypes(include=np.number).columns

        if len(num_cols) > 0:
            for col in num_cols:
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                outliers = df[(df[col] < (q1 - 1.5 * iqr)) | (df[col] > (q3 + 1.5 * iqr))]

                st.write(f"{col}: {len(outliers)} outliers")
        else:
            st.warning("⚠ No numeric columns available for outlier detection.")

        st.markdown("### 🤖 Summary")

        summary = f"""
        Dataset contains {df.shape[0]} rows and {df.shape[1]} columns.  
        Total missing values: {df.isnull().sum().sum()}.
        """
        st.info(summary)

else:
    st.info("📂 Please upload a CSV file to begin.")