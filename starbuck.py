
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.title('Starbucks 1 Store Directory App ☕')

# Raw file from Github #
DATA_URL = ('https://github.com/siriwatsc-debug/DADS5001-Streamlit/raw/main/directory.csv')

@st.cache_data
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
   
    data.rename(columns={'latitude': 'lat', 'longitude': 'lon'}, inplace=True)
    return data

# Run the app: streamlit run app.py

data_load_state = st.text('Loading data...')
# Load all data : set  nrows = None 
#data = load_data(10000)
data = load_data(nrows=None)

data_load_state.text("Done! (using st.cache_data)")

# Show rawdata if check box
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

#df = data.copy()
st.subheader('Map of Starbuck')

# ====================================================================
# Part 1 : (Map Visualization)
# ====================================================================
st.header("1. World Wide branches and retail")

# จัดการข้อมูลที่ไม่มีค่า Latitude/Longitude สำหรับการแสดงผลบนแผนที่
map_data = data.dropna(subset=['lat', 'lon'])

# แสดงแผนที่ (Streamlit มีฟังก์ชันสำหรับแสดงแผนที่จาก lat/lon โดยตรง)
st.map(map_data, latitude='Latitude', longitude='Longitude', zoom=1)

st.markdown("---")


# ====================================================================
# Part 2 : Top 10 ประเทศที่มีจำนวนร้านมากที่สุด (Bar Chart)
# ====================================================================
st.header("2. Top 10 countries with highest branches")

# คำนวณจำนวนร้านต่อประเทศ
country_counts = data['country'].value_counts().reset_index()
country_counts.columns = ['Country', 'Store Count']
top_10_countries = country_counts.head(10)

# สร้าง Bar Chart ด้วย Altair
chart_countries = alt.Chart(top_10_countries).mark_bar().encode(
    # เรียงลำดับจากมากไปน้อย
    x=alt.X('Store Count', title='branch'),
    y=alt.Y('Country', sort='-x', title='Country'),
    tooltip=['Country', 'Store Count'],
    # ใส่สีตาม Store Count
    color=alt.Color('Store Count', scale=alt.Scale(range='ramp')),
).properties(
    title='Number of Starbucks / Country (Top 10)'
).interactive() # ทำให้กราฟซูม/แพนได้

st.altair_chart(chart_countries, use_container_width=True)

st.markdown("---")



# ====================================================================
# Part 3 : สัดส่วนประเภทความเป็นเจ้าของ (Donut Chart)
# ====================================================================
st.header("3. Type of Ownership ")

# คำนวณสัดส่วน (คอลัมน์ 'ownership type' เป็นตัวพิมพ์เล็กจากการทำความสะอาดข้อมูล)
ownership_counts = data['ownership type'].value_counts().reset_index()
ownership_counts.columns = ['Ownership Type', 'Count']
total = ownership_counts['Count'].sum()
ownership_counts['Percentage'] = (ownership_counts['Count'] / total) * 100

# สร้าง Donut Chart ด้วย Altair
base = alt.Chart(ownership_counts).encode(
    theta=alt.Theta("Count", stack=True)
)

# แก้ไข: เปลี่ยนการใช้ alt.Tooltip().label(suffix='%') เป็น alt.Tooltip() แบบง่าย
# หรือใช้ alt.Tooltip('Percentage', format='.1f', title='Percentage (%)') เพื่อเพิ่ม % ใน title
pie = base.mark_arc(outerRadius=120, innerRadius=80).encode( # กำหนด innerRadius เพื่อให้เป็น Donut Chart
    color=alt.Color("Ownership Type", title="ประเภท"),
    order=alt.Order("Count", sort="descending"),
    # แก้ไขการแสดงผล Tooltip สำหรับ Percentage: ใช้ format เพื่อแสดงทศนิยม 1 ตำแหน่ง
    tooltip=["Ownership Type", "Count", alt.Tooltip('Percentage', format='.1f')]
).properties(
    title='Type of ownership'
)
# ข้อความแสดงเปอร์เซ็นต์
text = base.mark_text(radius=140).encode(
    text=alt.Text("Percentage", format=".1f"),
    order=alt.Order("Count", sort="descending"),
    color=alt.value("black")
)

# แสดงชาร์ต
st.altair_chart(pie, use_container_width=True)
