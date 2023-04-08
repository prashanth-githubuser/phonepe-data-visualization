import streamlit as st
import mysql.connector
from mysql.connector import Error
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import json
import pandas as pd

#---------------------------------(Importing Files from Database)------------------------------

indian_states = json.load(open("D:\Python\Project\Phonepe\phonepe\states_india.geojson", "r"))



@st.cache_data(ttl=300, show_spinner=False)
def import_files():
    data_frame = ['district_user_C', 'state_transaction_C', 'top_transaction_C', 'top_users_C']
    imported_files = []
    for name in data_frame:
        try:
            connection = mysql.connector.connect(host='localhost',
                                                    database='Phonepe',
                                                    user='root',
                                                    password='Root@0000')
            if connection.is_connected():
                cursor = connection.cursor()

                cursor.execute(f"SELECT * FROM {name}")
                records1 = cursor.fetchall()
                name = pd.DataFrame(records1,
                                columns=[i[0] for i  in cursor.description])
                
                imported_files.append(name)

                connection.commit()
                cursor.close()
                connection.close()
        except Error as e:
            print("Table Not found: ", e)
    print("Import completed")

    return imported_files


#===============================(Plotting Map)===============================
# -------------> Transaction
@st.cache_data(show_spinner="Plotting Map......")
def plot_map_transation(df:pd.DataFrame, year,quater):
    state_id_map = {}
    for feature in indian_states['features']:
        feature['id'] = feature['properties']['state_code'] # fetching the id from geojson file for each state
        state_id_map[feature['properties']['st_nm']] = feature['id']
        
    new_df_2 = df[(df['Year'] == int(year)) & (df['Quater']==quater)].groupby(['State', 'id']).aggregate({"Transacion_amount":sum}).reset_index()
    fig = px.choropleth(data_frame=new_df_2,
                    locations="id",
                    geojson=indian_states, 
                    color= "Transacion_amount",
                    hover_name="State",
                    color_continuous_scale=px.colors.sequential.Emrld, 
                    
                    scope='asia') #color_continuous_midpoint=6.925872e07, #YlGn, Aggrnyl_r

    fig.update_geos(fitbounds="locations", visible=False)
    return fig

# -------------> Users
@st.cache_data(show_spinner="Plotting Map......")
def plot_map_user(df:pd.DataFrame, year,quater):
    state_id_map = {}
    for feature in indian_states['features']:
        feature['id'] = feature['properties']['state_code'] # fetching the id from geojson file for each state
        state_id_map[feature['properties']['st_nm']] = feature['id']
        
    new_df_2 = df[(df['Year'] == int(year)) & (df['Quater']==quater)].groupby(['State', 'id']).aggregate({"Registered_user":sum}).reset_index()
    fig = px.choropleth(data_frame=new_df_2,
                    locations="id",
                    geojson=indian_states, 
                    color= "Registered_user",
                    hover_name="State",
                    color_continuous_scale=px.colors.sequential.Emrld, 
                    
                    scope='asia') #color_continuous_midpoint=6.925872e07, #YlGn, Aggrnyl_r

    fig.update_geos(fitbounds="locations", visible=False)
    return fig

# -------------> State transaction
@st.cache_data(show_spinner="Plotting Map......")
def plot_map_state_transation(df:pd.DataFrame,state, year,quater):
    state_id_map = {}
    for feature in indian_states['features']:
        feature['id'] = feature['properties']['state_code'] # fetching the id from geojson file for each state
        state_id_map[feature['properties']['st_nm']] = feature['id']
        
    new_df_2 = df[(df['State'] == state) &(df['Year'] == int(year)) & (df['Quater']==quater)].groupby(['State', 'id']).aggregate({"Transacion_amount":sum}).reset_index()
    fig = px.choropleth(data_frame=new_df_2,
                    locations="id",
                    geojson=indian_states, 
                    color= "Transacion_amount",
                    hover_name="State",
                    color_continuous_scale=px.colors.sequential.Emrld, 
                    
                    scope='asia') #color_continuous_midpoint=6.925872e07, #YlGn, Aggrnyl_r

    fig.update_geos(fitbounds="locations", visible=False)
    return fig


#===============================(Importing the required files from Db===============================

imported_files = import_files()
district_user = imported_files[0]
state_transaction = imported_files[1]
top_transaction = imported_files[2]
top_users = imported_files[3]



#===============================(Web page Setting)==============================================

st.set_page_config(layout='wide', initial_sidebar_state='expanded')

st.sidebar.header('Dashboard `version 1.0`')
nav = st.sidebar.radio('Select Option',["All India","State"]) 
st.sidebar.markdown('''---''') 

#===============================(Web page side bar options)==============================================

if nav == 'All India':
    

    st.sidebar.subheader('All India')

    all_india = st.sidebar.selectbox('Type', ('Transaction', 'Users'), key='all_india') 
    year = st.sidebar.selectbox('All India', ( '2022','2021','2020','2019','2018'), key='all_india_year') 
    quater = st.sidebar.selectbox('Period', ('Q4','Q3','Q2','Q1'), key='all_india_period') 

#======================================(Query)======================================


    #======================================>   Transaction 

    #All_total transaction value

    df_transaction_value = state_transaction[(state_transaction['Year'] == int(year)) 
                                            & (state_transaction['Quater']==quater)]\
                                            .groupby(["State", "id"]).aggregate({"Transacion_amount": sum}).reset_index()
    india_transaction_value = df_transaction_value.sum().tolist()



    #All_total transaction count

    df_transaction_count = state_transaction[(state_transaction['Year'] == int(year)) &
                                            (state_transaction['Quater']==quater)]\
                                            .groupby(["State", "id"])\
                                            .aggregate({"Transacion_count": sum}).reset_index()
    India_transaction_count = df_transaction_count.sum().tolist()



    #type

    transaction_type_india = state_transaction[(state_transaction['Year']== int(year)) & \
                                               (state_transaction["Quater"]==quater)].groupby("Transacion_type")\
                                                .aggregate({"Transacion_count" : sum})
    
    transaction_type_india = transaction_type_india.add_suffix('_Count').reset_index()
    transaction_type_india.set_index(transaction_type_india["Transacion_type"], inplace = True)
    transaction_type_india.rename(columns = {'Transacion_count_Count': 'Count'}, inplace = True)
    top_transaction_type = transaction_type_india[["Count"]].sort_values(by = "Count" ,ascending=False)\
                                                .head().style.format({"Count": '{:,.0f}'})


    #Top_10_states

    transaction_state_india = state_transaction[(state_transaction['Year']== int(year))&\
                                                (state_transaction["Quater"]==quater)].groupby("State")\
                                                .aggregate({"Transacion_count" : sum})
                                                
                                                
    transaction_state_india = transaction_state_india.sort_values(by= "Transacion_count", ascending=False).add_suffix('_Count').reset_index()
    transaction_state_india.set_index(transaction_state_india["State"], inplace = True)
    transaction_state_india.rename(columns = {'Transacion_count_Count': 'Count'}, inplace = True)
    transaction_state_india["Count"] = round((transaction_state_india['Count']/1e7), 2)
    top_10_states = transaction_state_india[["Count"]].sort_values(by = "Count" ,ascending=False).head(10).style.format({"Count": '{:,.2f} Cr'})

    #Top_10_district
    transaction_district_india = top_transaction[(top_transaction['Year']== int(year)) & (top_transaction["Quarter"]==quater)\
                                     & (top_transaction["Entity_type"]=="district")].groupby("District_pincode").aggregate({"Transacion_count" : sum})
    
    transaction_district_india = transaction_district_india.add_suffix('_Count').reset_index()
    transaction_district_india.rename(columns= {"District_pincode": "District"}, inplace = True)
    transaction_district_india.set_index(transaction_district_india["District"], inplace = True)
    transaction_district_india["Count (Cr)"] = round((transaction_district_india['Transacion_count_Count']/1e7), 2)
    top_10_districts = transaction_district_india[["District","Count (Cr)"]].sort_values(by = "Count (Cr)" ,ascending=False).head(5)#.style.format({"Count": '{:,.2f} Cr'})

    #======================================>    Users

    #All users
    users_across_india = district_user[(district_user["Year"] == int(year)) & (district_user["Quater"] == quater)]\
                    .aggregate({"Registered_user" : sum,"App_opening" : sum}).tolist()
    
    # Top 10 States
    #top_users
    top_users_by_state = top_users[(top_users['Year'] == int(year)) & (top_users['Quarter'] == quater)].groupby("State").aggregate({"Registered_users" : sum})
    top_users_by_state["Users (Cr)"] = round((top_users_by_state['Registered_users']/1e7), 2)
    top_10_user_states = top_users_by_state.sort_values(by='Users (Cr)', ascending=False).head(10)

    #top registered by district
    top_users_by_district = top_users[(top_users["Year"] == int(year)) & (top_users["Quarter"] == quater)
                                & (top_users["Entity_type"] == "district")].sort_values(by='Registered_users', ascending= False)
    top_users_by_district.set_index(top_users_by_district["District_pincode"], inplace = True)
    top_users_by_district["Registered_users (L)"] = round((top_users_by_district['Registered_users']/1e5), 2)
    top_10_users_by_district = top_users_by_district[[ "Registered_users (L)"]].head(10)    

#==============================================(Main Page)=======================================  

#--------------> Row I
    if all_india == 'Transaction':
        ''' ### Transaction'''

    elif all_india == "Users":
        ''' ### Users'''

    col1, col2 = st.columns(2)
    if all_india == 'Transaction':

        col1.metric("All PhonePe transactions", f"{India_transaction_count[-1]:,}")
        col2.metric("Total payment value", f"₹{(round(((india_transaction_value[-1]/1e7)))):,} Cr")

    elif all_india == "Users": 

        #PhonePe app opens in Q4 2022


        col1.metric("Registered PhonePe users till Q4 2022", f"{users_across_india[0]:,}")
        col2.metric("PhonePe app opens in Q4 2022", f"{users_across_india[1]:,}")

    '---'
#--------------> Row II 
    if all_india == 'Transaction': 

        map1 = plot_map_transation(state_transaction,year,quater)
        map1
    elif all_india == "Users": 
        map2 = plot_map_user(district_user, year, quater)
        map2
        pass

    '---'

#--------------> Row III
    col3, col4, col5 = st.columns(3)

    with col3:
        if all_india == 'Transaction':
            top_10_states

    with col4:
        if all_india == 'Transaction':
            top_transaction_type

    with col3:
        if all_india == "Users": 
            
           st.write(top_10_user_states['Users (Cr)']) 

    with col5:

        if all_india == 'Transaction':
            Q = []
            Quater = state_transaction["Quater"].unique()
            for Qs in Quater:
                temp = state_transaction[(state_transaction["Year"] == int(year)) & (state_transaction["Quater"]== Qs)].sort_values("Transacion_count", ascending=False).sum().tolist()
                Q.append(temp[5])

            data = Q
            keys = ['Q1', 'Q2', 'Q3', 'Q4']
            explode = (0.05, 0.05, 0.05, 0.05)
            palette_color = sns.color_palette('pastel')[0:5]
            my_circle = plt.Circle((0, 0), 0.75, color='white') 
            fig, ax = plt.subplots()
            ax.pie(data, labels=keys, colors=palette_color, autopct='%.0f%%', explode=explode)
            plt.title(f'Transaction Count Quater Comparison ({year})')  
            p = plt.gcf()
            p.gca().add_artist(my_circle)
            st.pyplot(fig)

    with col4:
        if all_india == 'Users':
           st.write(top_10_users_by_district) 
    
    with col5:
        try:
            if all_india == 'Users':
                Q = []
                Quater = district_user["Quater"].unique()
                for Qs in Quater:
                    temp = district_user[(district_user["Year"] == int(year)) & (district_user["Quater"]== Qs)].sort_values("Registered_user", ascending=False).sum().tolist()
                    Q.append(temp[5])

                data = Q
                keys = ['Q1', 'Q2', 'Q3', 'Q4']
                explode = (0.05, 0.05, 0.05, 0.05)
                palette_color = sns.color_palette('pastel')[0:5]
                my_circle = plt.Circle((0, 0), 0.75, color='white') 
                fig, ax = plt.subplots()
                ax.pie(data, labels=keys, colors=palette_color, autopct='%.0f%%', explode=explode)
                plt.title(f'User Count Quater Comparison ({year})')  
                p = plt.gcf()
                p.gca().add_artist(my_circle)
                st.pyplot(fig)
        except :
            st.info("Info Not Available for FY 2018",  icon="ℹ️")


#--------------> Row IV 
    with col3:
        if all_india == 'Transaction':
        #top_10_districts
            st.write(top_10_districts["Count (Cr)"])

    with col4:
        if all_india == 'Transaction':
       
            fig1=px.bar(top_10_districts, x="District", y="Count (Cr)")
            st.write(fig1)

'---'

if nav == 'State':
    st.sidebar.subheader('State')
    
    state = st.sidebar.selectbox('Select State', (state_transaction['State'].unique()), key='state') 
    year = st.sidebar.selectbox('Year', ('2022','2021','2020','2019','2018'), key='state_year') 
    quater = st.sidebar.selectbox('Period', ('Q4','Q3','Q2','Q1'), key='state_period') 

    #======================================(Query)======================================

    #======================================>   Transaction 
    #State transaction value

    df_transaction_value = state_transaction[(state_transaction['State'] == state)
                                            & (state_transaction['Year'] == int(year)) \
                                            & (state_transaction['Quater']==quater)]\
                                            .groupby(["State", "id"]).aggregate({"Transacion_amount": sum}).reset_index()
    state_transaction_value = df_transaction_value.sum().tolist()



    #State transaction count

    df_transaction_count = state_transaction[(state_transaction['State'] == state)  
                                            & (state_transaction['Year'] == int(year))\
                                            & (state_transaction['Quater']==quater)]\
                                            .groupby(["State", "id"])\
                                            .aggregate({"Transacion_count": sum}).reset_index()
    state_transaction_count = df_transaction_count.sum().tolist()

    #
    top_district = top_transaction[(top_transaction["State"]== state) & (top_transaction["Year"]== int(year)) & (top_transaction["Entity_type"] == "district") & (top_transaction["Quarter"] == quater)].sort_values(by = "Total_amount", ascending=False)
    top_district.set_index(top_district["District_pincode"], inplace = True)
    top_district["Count_value"] = round((top_district['Total_amount']/1e7), 2)
    top_district = top_district[["Count_value"]].head(10).style.format({"Count_value": '{:,.0f} Cr'})


    top_pin = top_transaction[(top_transaction["State"]== state) & (top_transaction["Year"]== int(year)) & (top_transaction["Entity_type"] == "pincode") & (top_transaction["Quarter"] == quater)].sort_values(by = "Total_amount", ascending=False)
    top_pin.set_index(top_pin["District_pincode"], inplace = True)
    top_pin["Count_value"] = round((top_pin['Total_amount']/1e7), 2)
    top_pin = top_pin[["Count_value"]].head(10).style.format({"Count_value": '{:,.0f} Cr'})


#==============================================(Main Page)=======================================  

#--------------> Row I
    if state:
        ''' ### Transaction'''

    col1, col2 = st.columns(2)
    if state:

        col1.metric("All PhonePe transactions", f"{state_transaction_count[-1]:,}")
        col2.metric("Total payment value", f"₹{(round(((state_transaction_value[-1]/1e7)))):,} Cr")
    st.markdown("---")
#--------------> Row II 
    if state: 
        st.markdown(f'''### Location:  {state} ''')
        map1 = plot_map_state_transation(state_transaction,state, year,quater)
        map1
    
    st.markdown("---")
        
#---------------> Row  III
    col3, col4, col5 = st.columns(3)

    with col3:
        if state:
            st.write(top_district)

    with col4:
        if state:
            st.write(top_pin)
            

    with col5:

        if state:
            Q = []
            Quater = state_transaction["Quater"].unique()
            for Qs in Quater:
                temp = state_transaction[(state_transaction["State"] == state) & (state_transaction["Year"] == int(year)) & (state_transaction["Quater"]== Qs)].sort_values("Transacion_count", ascending=False).sum().tolist()
                Q.append(temp[5])

            data = Q
            keys = ['Q1', 'Q2', 'Q3', 'Q4']
            explode = (0.05, 0.05, 0.05, 0.05)
            palette_color = sns.color_palette('pastel')[0:5]
            my_circle = plt.Circle((0, 0), 0.75, color='white') 
            fig, ax = plt.subplots()
            ax.pie(data, labels=keys, colors=palette_color, autopct='%.0f%%', explode=explode)
            plt.title(f'Transaction Count Quater Comparison ({year})')  
            p = plt.gcf()
            p.gca().add_artist(my_circle)
            st.pyplot(fig)



st.sidebar.markdown('''
---
Created with ❤️ by [Prashanth M](https://github.com/prashanth-githubuser).
''')








