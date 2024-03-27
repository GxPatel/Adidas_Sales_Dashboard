import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
import plotly.figure_factory as ff
import calendar
warnings.filterwarnings('ignore')

# Page Styling
st.set_page_config(page_title='Sales Dashboard', 
                   page_icon=':chart_with_upwards_trend:',
                   initial_sidebar_state='expanded', 
                   layout='wide')

# Dashboard Title
st.title(':bar_chart: Adidas Sales Dashboard')
vert_space = '<div style="padding: 10px 0px;"></div>'
st.markdown(vert_space, unsafe_allow_html=True)

# Reading data file
df = pd.read_csv("AdidasSalesdata.csv", encoding = "ISO-8859-1")

# Converting raw data column
df["Invoice Date"] = pd.to_datetime(df["Invoice Date"])

# Getting the min and max date 
startDate = pd.to_datetime(df["Invoice Date"]).min()
endDate = pd.to_datetime(df["Invoice Date"]).max()

col1, col2 = st.columns((2))
with col1:
    date1 = pd.to_datetime(st.date_input("Choose Start Date :date:", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("Choose End Date :date:", endDate))

df = df[(df["Invoice Date"] >= date1) & (df["Invoice Date"] <= date2)].copy()


# Filters picker
st.sidebar.header("Choose your filters:")

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

column1, column2 = st.columns((2))
with column1: # Category vs. Sales bar chart
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x="Product Category", y="Total Sales", text=['${:,.2f}'.format(x) for x in category_df["Total Sales"]],
                 template="simple_white")
    st.plotly_chart(fig, use_container_width=True, height=200)

with column2: # Region vs. Sales pie chart
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values = "Total Sales", names = "Region", hole = 0.5, template="seaborn")
    fig.update_traces(text = filtered_df["Region"], 
                      textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)


cl1, cl2 = st.columns((2))
with cl1: # Sales Method vs. Sales pie chart
    st.subheader("Sales Method wise Sales")
    fig = px.pie(filtered_df, values = "Total Sales", names = "Sales Method", hole = 0.5)
    fig.update_traces(text = filtered_df["Sales Method"], 
                      textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)


with cl2: # Profit vs. Month_Year Line chart 
    st.subheader('Trend of Profit Over Time')
    filtered_df['Invoice Date'] = pd.to_datetime(filtered_df['Invoice Date'])
    sales_by_date = filtered_df.groupby(filtered_df['Invoice Date'].dt.to_period('M'))['Operating Profit'].sum().reset_index()
    sales_by_date['Invoice Date'] = sales_by_date['Invoice Date'].dt.to_timestamp()
    fig = px.line(sales_by_date, x='Invoice Date', y='Operating Profit', labels={'Invoice Date': 'Months', 'Operating Profit': 'Profit'}, template='gridon')
    st.plotly_chart(fig,use_container_width=True)


filtered_df.rename(columns={"ï»¿Retailer": "Retailer"}, inplace=True) # just for efficiency
chart1, chart2 = st.columns((2))
with chart1: # Retailer vs. sales pie chart
    st.subheader('Retailer wise Sales')
    fig = px.pie(filtered_df, values = "Total Sales", names = "Retailer", template = "plotly_dark")
    fig.update_traces(text = filtered_df["Retailer"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)

with chart2: # Gender vs. sales pie chart
    st.subheader('Gender wise Sales')
    fig = px.pie(filtered_df, values = "Total Sales", names = "Gender Type", template = "gridon")
    fig.update_traces(text = filtered_df["Gender Type"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)


# Summary table of monthly sales
st.subheader(":point_right: Monthly Category Sales")
with st.expander("Expand to View Table"):
    filtered_df["month"] = filtered_df["Invoice Date"].dt.month_name()
    months_chronological = [calendar.month_name[i] for i in range(1, 13)]
    category_Year = pd.pivot_table(data=filtered_df, values='Total Sales', index=['Product Category'], columns='month', aggfunc='sum', fill_value=0)[months_chronological]
    st.write(category_Year.style.background_gradient(cmap="Blues"))


# Scatter plot
fig = px.scatter(filtered_df, x = "Total Sales", y = "Operating Profit", size = "Units Sold")
fig['layout'].update(title="Relationship between Sales and Profit",
                       titlefont = dict(size=20),xaxis = dict(title="Sales",titlefont=dict(size=19)),
                       yaxis = dict(title = "Profit", titlefont = dict(size=19)))
st.plotly_chart(fig, use_container_width=True)


# Raw Data
with st.expander("Expand to View Raw Data"):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Blues"))

# Download orginal DataSet
csv = df.to_csv(index = False).encode('utf-8')
st.download_button('Download Data', data = csv, file_name = "Data.csv",mime = "text/csv")