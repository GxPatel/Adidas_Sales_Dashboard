import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
import plotly.figure_factory as ff
import calendar
import matplotlib
warnings.filterwarnings('ignore')

# Page Styling
st.set_page_config(page_title='Sales Dashboard', 
                   page_icon=':chart_with_upwards_trend:',
                   initial_sidebar_state='expanded', 
                   layout='wide')

# Dashboard Title
st.write("### :bar_chart: Adidas Sales Dashboard")
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 300px !important;
        }
        .block-container {
                    padding-top: 3rem;
                    padding-bottom: 2rem;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """, 
    unsafe_allow_html=True
    )

# Reading data file
df = pd.read_csv(r"C:\Users\gp158\Desktop\Projects\Adidas_Sales_Dashboard\AdidasSalesdata.csv", encoding = "ISO-8859-1")

# Converting raw data column
df["Invoice Date"] = pd.to_datetime(df["Invoice Date"])

# Getting the min and max date 
startDate = pd.to_datetime(df["Invoice Date"]).min()
endDate = pd.to_datetime(df["Invoice Date"]).max()

# Filters picker
st.sidebar.header("Choose your filters:")

date1 = pd.to_datetime(st.sidebar.date_input("Choose Start Date:", startDate))
date2 = pd.to_datetime(st.sidebar.date_input("Choose End Date:", endDate))
df = df[(df["Invoice Date"] >= date1) & (df["Invoice Date"] <= date2)].copy()

# Dropdown for Region
region = st.sidebar.multiselect("Pick the Region(s)", df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

# Dropdown for State
state = st.sidebar.multiselect("Pick the State(s)", df2["State"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]

# Dropdown for City
city = st.sidebar.multiselect("Pick the City(s)",df3["City"].unique())

# Filter the data based on Region, State and City
if not region and not state and not city:
    filtered_df = pd.DataFrame(df)
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]

category_df = filtered_df.groupby(by = ["Product Category"], as_index = False)["Total Sales"].sum()

column1, column2, column3 = st.columns((3))
with column1: # Category vs. Sales bar chart
    st.write("##### Category wise Sales")
    #st.subheader("Category wise Sales", text_size="24px")
    fig = px.bar(category_df, x="Product Category", y="Total Sales", text=['${:,.2f}'.format(x) for x in category_df["Total Sales"]],
                 template="simple_white", width=800, height=300)
    st.plotly_chart(fig, use_container_width=True)

with column2: # Region vs. Sales pie chart
    st.write("##### Region wise Sales")
    fig = px.pie(filtered_df, values = "Total Sales", names = "Region", hole = 0.5, template="seaborn", width=600, height=300)
    fig.update_traces(text = filtered_df["Region"], 
                      textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)

with column3: # Sales Method vs. Sales pie chart
    st.write("##### Sales Method wise Sales")
    fig = px.pie(filtered_df, values = "Total Sales", names = "Sales Method", hole = 0.5, width=400, height=300)
    fig.update_traces(text = filtered_df["Sales Method"], 
                      textposition = "inside")
    st.plotly_chart(fig,use_container_width=True)


cl1, cl2 = st.columns((2))
with cl1: # Profit vs. Month_Year Line chart 
    st.write('##### Trend of Profit Over Time')
    filtered_df['Invoice Date'] = pd.to_datetime(filtered_df['Invoice Date'])
    sales_by_date = filtered_df.groupby(filtered_df['Invoice Date'].dt.to_period('M'))['Operating Profit'].sum().reset_index()
    sales_by_date['Invoice Date'] = sales_by_date['Invoice Date'].dt.to_timestamp()
    fig = px.line(sales_by_date, x='Invoice Date', y='Operating Profit', labels={'Invoice Date': 'Months - Years', 'Operating Profit': 'Profit (USD)'}, 
                template='gridon', width=600, height=300)
    st.plotly_chart(fig,use_container_width=True)

filtered_df.rename(columns={"ï»¿Retailer": "Retailer"}, inplace=True) # just for efficiency
with cl2: # Retailer vs. sales pie chart
    st.write('##### Retailer wise Sales')
    fig = px.pie(filtered_df, values = "Total Sales", names = "Retailer", template = "plotly_dark", 
                width=600, height=300)
    fig.update_traces(text = filtered_df["Retailer"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)


# Raw Data
with st.expander("Expand to View Raw Data"):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Blues"))

# Download orginal DataSet
csv = df.to_csv(index = False).encode('utf-8')
st.download_button('Download Data', data = csv, file_name = "Data.csv",mime = "text/csv")

# Footer Styling
footer = st.empty()
footer.markdown(
"""<style>
a:link , a:visited{
color: blue;
background-color: transparent;
text-decoration: underline;
}

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: sticky;
bottom: 0;
z-index: 1000;
width: 100%;
background-color: rgba(255,2555,255,35);
color: black;
text-align: center
}
</style>
<div class="footer">
<p> © 2024 All rights reserved. <a style='display: block; text-align: center;' href="https://github.com/GxPatel" target="_blank"> GxPatel </a></p>
</div>
""",
unsafe_allow_html=True)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 