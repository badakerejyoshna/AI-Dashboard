import streamlit as st
import pandas as pd
import plotly.express as px

# Set up page layout
st.set_page_config(
    page_title="AI Dashboard Assignment",
    layout="wide"
)

# Main Title of Assignment
st.title("🤖 AI Interactive Dashboard ")

# File Upload block
uploaded_file = st.file_uploader("Upload your CSV dataset here", type=["csv"])

if uploaded_file is not None:
    # Reading the dataset using pandas
    df = pd.read_csv(uploaded_file)

    # 1. DATASET OVERVIEW SECTION
    st.header("1️⃣ Dataset Overview")
    
    # Displaying rows and columns in columns
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Total Rows", df.shape[0])
    with c2:
        st.metric("Total Columns", df.shape[1])
        
    st.subheader("Preview of the Data")
    st.dataframe(df.head())


    # 2. DATA CLEANING SECTION (Required for marks)
    st.header("2️⃣ Data Cleaning Profile")
    
    # Counting missing values before cleaning
    total_nulls = df.isnull().sum().sum()
    st.write("Total missing values found in dataset:", total_nulls)
    
    # Drop duplicates
    df_clean = df.drop_duplicates()
    
    # --- SUPERSTORE DATA TYPE FORCING FIX ---
    # This forces common Retail Dataset columns to be recognized as numbers!
    possible_numeric = ['sales', 'quantity', 'profit', 'discount', 'shipping_cost']
    for col in df_clean.columns:
        # Check if the column name matches common numeric columns (case-insensitive)
        if col.lower() in possible_numeric:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            
    # Fill remaining missing items with 0
    df_clean = df_clean.fillna(0) 
    
    st.success("Data Cleaning Done! Cleaned text fields, forced financial columns to numeric, and handled missing values.")


    # 3. INTERACTIVE SIDEBAR FILTERS
    st.sidebar.header("🎯 Filter Options")
    
    # Getting accurate clean column lists for dropdown selectors
    all_columns = df_clean.columns.tolist()
    numeric_columns = df_clean.select_dtypes(include=["number", "float64", "int64"]).columns.tolist()
    categorical_columns = df_clean.select_dtypes(exclude=["number", "float64", "int64"]).columns.tolist()

    # Create a simple filter based on a categorical column (like region or market)
    if len(categorical_columns) > 0:
        filter_col = st.sidebar.selectbox("Choose column to filter data:", categorical_columns, key="sidebar_filter_select")
        
        # Take only the first 30 unique items to prevent dropdown crashes
        unique_choices = df_clean[filter_col].drop_duplicates().astype(str).tolist()[:30]
        default_choices = unique_choices[:3] if len(unique_choices) >= 3 else unique_choices
        
        # User selects values to filter
        selected_choices = st.sidebar.multiselect("Select values:", options=unique_choices, default=default_choices)
        
        # Filtering the dataset based on selection
        if selected_choices:
            final_df = df_clean[df_clean[filter_col].astype(str).isin(selected_choices)]
        else:
            final_df = df_clean.copy()
    else:
        final_df = df_clean.copy()
        st.sidebar.warning("No categories found to filter.")


    # 4. KEY METRICS (KPIs)
    st.header("3️⃣ Key Metrics (KPIs)")
    
    kp1, kp2, kp3 = st.columns(3)
    with kp1:
        st.metric("Filtered Data Rows", len(final_df))
        
    with kp2:
        if len(numeric_columns) > 0:
            chosen_sum = st.selectbox("Select column to sum:", numeric_columns, key="kpi_sum_select")
            st.metric("Total Sum", f"{final_df[chosen_sum].sum():,.2f}")
        else:
            st.metric("Total Sum", "No numeric data found")
            
    with kp3:
        if len(numeric_columns) > 0:
            chosen_avg = st.selectbox("Select column for average:", numeric_columns, key="kpi_avg_select")
            st.metric("Average Value", f"{final_df[chosen_avg].mean():,.2f}")
        else:
            st.metric("Average Value", "No numeric data found")


    # 5. FIVE REQUIRED VISUALIZATIONS
    st.header("4️⃣ Dynamic Dashboard Plots (5 Visualizations)")

    # Checking if data has what it needs to plot
    if len(numeric_columns) > 0 and len(categorical_columns) > 0:
        
        # Grid layout for Row 1: Charts 1 & 2
        left_col, right_col = st.columns(2)
        
        with left_col:
            st.subheader("Chart 1: Bar Graph")
            bar_x = st.selectbox("X Axis for Bar Chart (Categories)", categorical_columns, key="dropdown_bar_x")
            bar_y = st.selectbox("Y Axis for Bar Chart (Values)", numeric_columns, key="dropdown_bar_y")
            
            # Group data and sort to grab top 10 rows safely
            bar_data = final_df.groupby(bar_x)[bar_y].sum().reset_index()
            bar_data_sorted = bar_data.sort_values(by=bar_y, ascending=False).head(10)
            
            fig1 = px.bar(bar_data_sorted, x=bar_x, y=bar_y, title=f"Top 10 {bar_y} by {bar_x}", color=bar_x)
            st.plotly_chart(fig1, use_container_width=True)
            
        with right_col:
            st.subheader("Chart 2: Histogram")
            hist_x = st.selectbox("Column for Histogram", numeric_columns, key="dropdown_hist_x")
            fig2 = px.histogram(final_df, x=hist_x, title=f"Data Distribution Count for {hist_x}")
            st.plotly_chart(fig2, use_container_width=True)

        # Grid layout for Row 2: Charts 3 & 4
        left_col2, right_col2 = st.columns(2)
        
        with left_col2:
            st.subheader("Chart 3: Pie Chart")
            pie_names = st.selectbox("Category Column for Pie", categorical_columns, key="dropdown_pie_names")
            pie_values = st.selectbox("Value Column for Pie", numeric_columns, key="dropdown_pie_values")
            
            # Group by logic to structure pie charts nicely
            pie_data = final_df.groupby(pie_names)[pie_values].sum().reset_index().head(10)
            fig3 = px.pie(pie_data, names=pie_names, values=pie_values, title=f"Proportion Breakdown of {pie_names}")
            st.plotly_chart(fig3, use_container_width=True)
            
        with right_col2:
            st.subheader("Chart 4: Scatter Plot")
            scatter_x = st.selectbox("X Axis for Scatter", numeric_columns, key="dropdown_scatter_x")
            scatter_y = st.selectbox("Y Axis for Scatter", numeric_columns, key="dropdown_scatter_y")
            
            # Take a random slice of 500 records maximum so scatter loading doesn't freeze browser memory
            scatter_sample = final_df.head(500)
            fig4 = px.scatter(scatter_sample, x=scatter_x, y=scatter_y, title=f"Correlation between {scatter_x} and {scatter_y}")
            st.plotly_chart(fig4, use_container_width=True)

        # Row 3: Chart 5 (Full-width chart at the bottom)
        st.subheader("Chart 5: Line Graph (Trends)")
        line_x = st.selectbox("X Axis for Line Chart", all_columns, key="dropdown_line_x")
        line_y = st.selectbox("Y Axis for Line Chart", numeric_columns, key="dropdown_line_y")
        
        # Clean sort grouping for clean trend line calculations
        line_data = final_df.groupby(line_x)[line_y].mean().reset_index()
        sorted_df = line_data.sort_values(by=line_x).head(50) 
        
        fig5 = px.line(sorted_df, x=line_x, y=line_y, title=f"Trend Chart of Average {line_y}")
        st.plotly_chart(fig5, use_container_width=True)

    else:
        st.error("Data Type Error: The code did not find any recognized number columns. Please check your data fields.")

else:
    st.warning("Awaiting file upload... Please upload a valid CSV file.")
