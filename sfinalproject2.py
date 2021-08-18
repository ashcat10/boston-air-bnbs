"""
Name: Ashley Catoggio
CS230: Section SN2S
Data: Boston AirBnb Listings
URL:

Description:

This program will give users some basic information about the AirBnBs in Boston, MA. There is a map that displays
the location of the AirBnBs, having darker and larger bars where there are more AirBnBs. Additionally, users
can filter another map by specific neighborhood. There is also statistics and a bar chart to show the users the
availability in each neighborhood. Those who stay at AirBnBs often like basing their decisions on the amount of
reviews; therefore, there is information based on the number of reviews a user would like. There is also a lot
of information regarding the prices of AirBnBs as price is an important factor. There is an average price per
neighborhood, percentiles, and a place for users to filter by the specific price they want. Lastly, there are
a few more tables and charts in the main frame for users to look at once they open the application.
"""
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb
import plotly.graph_objects as go
import pydeck as pdk
sb.set()

def get_data(): #Gets all AirBnB data from excel file
    data = pd.read_csv("listings.csv")
    return data

def neighborhoods(): #Gets nonrepetitive list of all Boston neighborhoods in column "neighbourhood"
    neighborhoods = get_data()["neighbourhood"]
    neighborhood_list = [] #Create list to store values in from for loop below
    for i in neighborhoods:
        if i not in neighborhood_list:
            neighborhood_list.append(i) #Add neighborhood if it is not already in the list
    neighborhoods = neighborhood_list
    return neighborhoods

def display(): #Prints the title in main frame and sidebar
    st.title("*AirBnBs in Boston, MA*") #Added * to make italics
    st.sidebar.title("*AirBnB Information and Data*") #Added * to make italics

def image(img, description): #Prints skyline of Boston with a caption, parameter values at end of code
    sidebar = st.sidebar.image(img, caption=description)
    return img

def boston_map(): #Returns map of all Boston AirBnBs
    map_header = st.sidebar.subheader("Map of all AirBnBs in Boston, MA:") #Sidebar title for map
    all_button = st.sidebar.button("Map: All", key='maps') #Button to return the map
    df = get_data()
    if all_button:
        st.subheader("Map of all AirBnBs in Boston,MA") #Title of map displayed in main frame
        st.write(f"The total number of AirBnBs in Boston: {str(len(df.name))}")  # Prints total number of AirBnBs in Boston
        midpoint = [np.average(df["latitude"]), np.average(df["longitude"])] #Middle of the latitudes/longitudes
        st.pydeck_chart(pdk.Deck(map_style="mapbox://styles/mapbox/light-v9", #Type of map
                                 initial_view_state={"latitude": midpoint[0], "longitude": midpoint[1], "zoom": 11,
                                                     "pitch": 50, }, #Map view
                                 layers=[pdk.Layer("HexagonLayer", data=df[["latitude", "longitude"]],
                                                   get_position=["longitude", "latitude"], radius=200,
                                                   elevation_scale=4,elevation_range=[0, 1000], pickable=True,
                                                   extruded=True, )])) #Displays Hexagon bars on map
    return map_header, all_button

def specific_map(): #Returns map of specific neighborhood AirBnBs
    specific_header = st.sidebar.subheader("Map of AirBnBs in Neighborhoods:") #Sidebar title for specific map
    map_button = st.sidebar.button("Map:Specific Neighborhood", key='map') #Button to return the map
    df = get_data()
    neighborhood_select = st.sidebar.selectbox(label="Neighborhoods", options=neighborhoods()) #Selectbox for user to choose specific neighborhood
    filtered_data = df[df["neighbourhood"] == neighborhood_select] #Map only shows specific neighborhood chosen
    if map_button:
        st.subheader(f"Map of all AirBnBs in {neighborhood_select}, MA") #Title of map in the main frame
        st.write(f"The total number of AirBnBs in {neighborhood_select}: "
                 f"{str(len(df[(df.neighbourhood == neighborhood_select)]))}") #Prints total number of AirBnBs in that neighborhood
        midpoint = [np.average(df["latitude"]), np.average(df["longitude"])] #Middle of the latitudes/longitudes
        st.pydeck_chart(pdk.Deck(map_style="mapbox://styles/mapbox/light-v9", #Type of map
                                 initial_view_state={"latitude": midpoint[0], "longitude": midpoint[1], "zoom": 11,
                                                     "pitch": 50, },  #Map view
                                 layers=[pdk.Layer("HexagonLayer", data=filtered_data[["latitude", "longitude"]],
                                                   get_position=["longitude", "latitude"], radius=200, elevation_scale=4,
                                                   elevation_range=[0, 1000], pickable=True, extruded=True, )])) #Displays Hexagon bars on map
    return map_button, neighborhood_select, specific_header

def neighborhood_availability(): #Returns graph and percentiles (based on what button user clicks)
    availability_header = st.sidebar.subheader("365 Availability Statistics:") #Sidebar title for availability
    chart_button = st.sidebar.button("Neighborhood Availability Graph", key='neighborhood_graph') #Button to return bar graph
    availability_button = st.sidebar.button("Neighborhood Availability Stats", key='availability') #Button to return percentiles
    df = get_data()
    neighborhood = st.sidebar.selectbox(label="Neighborhoods:", options=neighborhoods()) #Selectbox for user to choose specific neighborhood
    if chart_button: #Graph Button
        st.subheader("Availability Chart") #Title in main frame
        df.query("availability_365>0").groupby("neighbourhood").availability_365.mean().plot.bar(rot=0).set(
            title="Average availability by neighborhood",
            xlabel="Neighborhood",
            ylabel="Avg. availability (in no. of days)") #Bar chart
        st.set_option('deprecation.showPyplotGlobalUse', False) #Stops a warning from popping up
        plt.xticks(rotation=90) #Rotates x-axis labels to 90 degrees
        st.pyplot()
    if availability_button: #Percentile Button
        st.subheader(f"{neighborhood} Availability Statistics:")  #Title in main frame
        information= df.query(f"""neighbourhood==@neighborhood""").availability_365.describe\
            (percentiles=[.25, .5, .75,]).to_frame() #Percentiles of availbility for specific neighborhood
        chart = st.table(information)

def reviews(): #Returns information based on number of reviews
    review_header = st.sidebar.subheader("Review Info of all AirBnBs:") #Title in sidebar
    review_button = st.sidebar.button("Review Information", key='review') #Button to return table
    df = get_data()
    minimum = st.sidebar.number_input("Minimum", min_value=0) #Minimum reviews
    maximum = st.sidebar.number_input("Maximum", min_value=0, value=5) #Maximum reviews
    if review_button:
        st.subheader("AirBnB listings by # of reviews") #Title in mainframe
        if minimum > maximum: #Prints error message
            st.error("Please enter a valid range")
        else: #Sorts information to come up in table
            df.query("@minimum<=number_of_reviews<=@maximum").sort_values("number_of_reviews", ascending=False).head(200)[["name", "number_of_reviews", "neighbourhood", "host_name", "room_type", "price"]]

def average_prices(): #Returns average price per neighborhood and price statistics per neighborhood
    average_header = st.sidebar.subheader("Prices in Neighborhoods:") #Title in sidebar
    distribution_button = st.sidebar.button("Get Average Price Table", key='average') #Button for average price per neighborhood table
    stats_button = st.sidebar.button("Get Price Statistics per Neighborhood", key='stats') #Button for price statistics per neighborhood
    data = get_data()
    data_new = data.rename(columns={'name': 'Name', 'host_name': 'Host Name', 'neighbourhood': 'Neighbourhood',
                                    'price': 'Price','availability_365': 'Availability 365'}) #Renames columns
    neighborhood = st.sidebar.selectbox(label="Neighborhood:", options=neighborhoods()) #Selectbox for user to choose specific neighborhood
    if distribution_button:
        st.subheader("Average Prices of Each Neighborhood in Highest to Lowest Order:") #Title in main frame
        st.dataframe(data_new.groupby("Neighbourhood").Price.mean().reset_index().round(2).sort_values
                     ("Price", ascending=False).assign(Avgerage_Price=lambda x:x.pop("Price").apply(lambda y: "%.2f" % y))) #Returns table
    if stats_button:
        st.subheader(f"{neighborhood} Price Statistics:") #Tile in main frame
        information = data.query(f"""neighbourhood==@neighborhood""").price.describe(percentiles=[.25, .5, .75]).to_frame() #Calculates price percentiles
        chart = st.table(information) #Returns table of price percentiles

def information_table(): #Overall data in main frame
    data = get_data()
    information_header = st.subheader("Data at a glance:") #Title in main frame
    data_new = data.rename(columns={'name':'Name','host_name':'Host Name','neighbourhood':'Neighbourhood','price':'Price','availability_365':'Availability 365'}) #Renames columns
    figure = go.Figure(data=go.Table(header=dict(values=list(data_new           #Uses plotly to format table with information
                                                             [['Name','Host Name', 'Neighbourhood', 'Price','Availability 365']]
                                                             .columns),fill_color='lightsteelblue',align='center'),
                                     cells=dict(values=[data.name, data.host_name, data.neighbourhood, data.price,
                                                        data.availability_365], fill_color='gainsboro', align='center')))
    figure.update_layout(margin=dict(l=10,r=15,b=1,t=1)) #Adds specific margins
    st.write(figure)

def pivot_table(): #Pivot table of average price based on room type in each neighborhood in main frame
    pivot = st.subheader("Average Prices for room type in each neighborhood:") #Tille in main frame
    df = get_data()
    table = pd.pivot_table(df,index=["neighbourhood","room_type"], values=["price"]) #Returns pivot table
    table_new = table.style.format({'price':'${0:.2f}'}) #Formats pivot table prices
    st.write(table_new)

def price_filters():     #Returns information based on price range in main frame
    data = get_data()
    st.subheader("Filter by price:")      #Tile in main frame
    data1= data[['name','neighbourhood','price']]       #Gets specific columns from data
    data_new = data1.rename(columns={'name':'Name','neighbourhood':'Neighbourhood','price':'Price'})  #Renames columns
    price = st.slider('Low Prices',float(data1.price.min()),float(data1.price.max()))        #Low end of price range
    price2 = st.slider('High Prices',float(data1.price.min()),float(data1.price.max()))     #High end of price range
    filtered_data = data_new[(data_new['Price'] >= price) & (data_new['Price']<= price2)]    #Filters data based on ranges
    st.write(filtered_data.sort_values('Price', ascending=True))                       #Sorts table from lowest to highest

#Returns functions
display()
image("skyline.jpg", "Skyline of Boston")
boston_map()
specific_map()
neighborhood_availability()
reviews()
average_prices()
information_table()
pivot_table()
price_filters()






