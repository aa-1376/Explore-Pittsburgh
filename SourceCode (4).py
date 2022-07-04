#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Team: NumPy-rates

Application: Things to do in Pittsburgh! 

Source Code 
"""

######## Helper functions for restaurant query
# Pull restaurant data using Yelp API
def get_restaurant_data():
    ''' 
    PURPOSE: To extract data on restaurants in Pittsburgh from Yelp using the Yelp API. 
    
    INPUTS: Takes no inputs, as all it needs is the built-in API key. 
    
    OUTPUTS: Returns a clean, analysis-ready dataset on restaurants in the Pittsburgh area. 
            Variables included are restaurant name, price level, rating, number of reviews, and location.
    '''
    
    # imports
    import requests
    import pandas as pd
    
    
    #  API key
    MY_API_KEY = "yxtiFnUlM7jPiP71RODtgFahfgH2gMkw5yzyww77h1Ad-s8uzE_gPUNsKk-6EribK8OBSi4lKVXzW8FpJFs0m4N-95zH6IReGETi9jYyr80H8393bje9GZTa-qJPYXYx" 
    
    headers = {'Authorization': f"Bearer {MY_API_KEY}"}
    url = 'https://api.yelp.com/v3/businesses/search'# endpoint url
    location = "Pittsburgh"
    params = {'location': location, 'limit': 50}
    
    # extract data via API
    resp = requests.get(url, headers=headers, params = params)
    
    # convert JSON object to pandas dataFrame
    dictr = resp.json()
    recs = dictr['businesses']
    df = pd.json_normalize(recs)
    
    ### data cleaning
    # restricting data to only a few variables of interest
    keep_list = ["name", "is_closed", "review_count", "categories", "rating","price", "location.display_address", "coordinates.latitude", "coordinates.longitude"]
    df_filtered = df.copy()
    df_filtered = df_filtered[keep_list]
    
    # adding cuisine type
    cuisine_type = []
    for i in range(0,len(df_filtered)): 
        category = df_filtered.iloc[i]['categories'][0]['title']
        cuisine_type.append(category)
    
    df_filtered['cuisine'] = cuisine_type 
    
    # removing rows that are not actually restaurants 
    not_food_index = df_filtered[(df_filtered['cuisine'] == 'Art Museums') | (df_filtered['cuisine'] == 'Museums') | (df_filtered['cuisine'] == 'Botanical Gardens') | (df_filtered['cuisine'] == 'Landmarks & Historical Buildings')].index
    df_filtered.drop(not_food_index, inplace = True) 
    
    return(df_filtered)



# Run restaurant query: Ask user for input, and return result as a map 
def restaurant_query(data):
    ''' 
    PURPOSE: to return restaurants and their locations based on what types of restaurants the user is interested in. 
    
    INPUTS: takes the output of get_restaurants_data() 
    
    OUTPUT: Displays a map with the restaurants matching the user-search criteria with markers including restaurant name and address. 
    '''
    # imports
    import plotly.express as px
    import plotly.io as pio
    pio.renderers.default='browser' 
    
    import pandas as pd
    import geopandas as gpd
    from shapely.geometry import Point

    
    # start query: ask user for restaurant specifications including price range, minimum desired rating, and minimum desired review count 
    print('\nWhat types of restaurants are you looking for?')
    price_parameter = input('\nEnter Price: $, $$, $$$, or $$$$: ')
    rating_parameter = float(input('\nEnter lowest desired rating (ex. Enter 4.5 if you only want to see restaurants rated 4.5 or higher: '))
    review_count_parameter = int(input('\nEnter lowest desired review count (ex. Enter 100 if you want restaurants with at least 100 ratings: '))
    
    # filter dataset for user search inputs. If no results are found, ask the user for different search parameters 
    queried_list = data[(data.price == price_parameter) & (data.rating >= rating_parameter) & (data.review_count >= review_count_parameter)]
    queried_list = queried_list[['name', 'location.display_address','cuisine', 'price', 'rating', 'review_count', 'coordinates.longitude', 'coordinates.latitude']]
    
    while len(queried_list) == 0: 
        print("\nSorry, there are no restaurants matching your search criteria. Please search again.")
        
        print('\nWhat types of restaurants are you looking for?')
        price_parameter = input('\nEnter Price: $, $$, $$$, or $$$$: ')
        rating_parameter = float(input('\nEnter lowest desired rating (ex. Enter 4.5 if you only want to see restaurants rated 4.5 or higher: '))
        review_count_parameter = int(input('\nEnter lowest desired review count (ex. Enter 100 if you want restaurants with at least 100 ratings: '))
        
        queried_list = data[(data.price == price_parameter) & (data.rating >= rating_parameter) & (data.review_count >= review_count_parameter)]
        queried_list = queried_list[['name', 'location.display_address','cuisine', 'price', 'rating', 'review_count', 'coordinates.longitude', 'coordinates.latitude']]
        
        if len(queried_list) > 0:
            break
    
    # generating output as an interactive map, displaying restaurant name, location, cuisine type, price, rating, and review count 
    crs = ('epsg:4326') # defining coordinate projection system 
    geometry = [Point(xy) for xy in zip(queried_list['coordinates.longitude'], queried_list['coordinates.latitude'])]
    geo_df = gpd.GeoDataFrame(queried_list, crs = crs, geometry = geometry)
    fig = px.scatter_mapbox(geo_df, lat=geo_df.geometry.y, lon=geo_df.geometry.x, 
                        hover_name="name", hover_data=["location.display_address", "cuisine", "price", "rating", "review_count"],
                        color_discrete_sequence=["fuchsia"], zoom=10)
    fig.update_layout(mapbox_style="open-street-map")
    fig.show()



######## Helper functions for art fixture query
# Import art data from CSV 
def get_art_data():#Imports art database from csv file
    ''' 
    PURPOSE: Imports art database from csv file
    
    INPUTS: takes no input
    
    OUTPUT: Returns cleaned, analysis ready dataset on art installations 
    '''
    # imports
    import pandas as pd
    import numpy as np
    
    # import CSV
    art_database_raw = pd.read_csv('art_data.csv')#reads the csv file into spyder
    
    # clean data 
    art_database = art_database_raw.fillna('Not Available')#changes all empty cells to string 'Not Available'
    art_database = art_database[(art_database['latitude'] != "Not Available") | (art_database['longitude'] != "Not Available")]#removes places with no latitude/longitude data from our data. Since our display is on interactive map the lat and long data points are necessary 
    
    return(art_database)


# Ask for user input 
def art_search(x,y, art_database):
    ''' 
    PURPOSE: Queries the art database for results based on user specifications from art_query(). This function is embedded in art_query(). Returns a map with results.
    
    INPUTS: User specifications from art_query(), output from get_art_data()
    
    OUTPUT: Returns an interactive map of art installations, and includes details on the artwork, the artist, and the neighborhood. 
    '''
   
    # imports
    import plotly.express as px
    import plotly.io as pio
    pio.renderers.default='browser' 
    
    import pandas as pd
    import geopandas as gpd
    from shapely.geometry import Point

    
    if y=='1':#creates if condition for when user wants to search by entering a neighbourhood he wants to visit the art installation in 
        result = art_database[art_database['neighborhood'] == x]
        
        # generating output on an interactive map of all art locations in the neighbourhood the user wants to vist 
        crs = ('epsg:4326') # defining coordinate projection system 
        geometry = [Point(xy) for xy in zip(result['longitude'], result['latitude'])]
        geo_df = gpd.GeoDataFrame(result, crs = crs, geometry = geometry)
        fig = px.scatter_mapbox(geo_df, lat=geo_df.geometry.y, lon=geo_df.geometry.x, 
                        hover_name="title", hover_data=["artist_name", "art_type", "neighborhood"],# identifies columns that should be displayed in the result
                        color_discrete_sequence=["fuchsia"], zoom=10)
        fig.update_layout(mapbox_style="open-street-map")
        fig.show()

    elif y=='2': 
        
        result = art_database[art_database['artist_name'] == x]
        
        # generating output on an interactive map of all art locations by the artist name the user identifies
        crs = ('epsg:4326') # defining coordinate projection system 
        geometry = [Point(xy) for xy in zip(result['longitude'], result['latitude'])]
        geo_df = gpd.GeoDataFrame(result, crs = crs, geometry = geometry)
        fig = px.scatter_mapbox(geo_df, lat=geo_df.geometry.y, lon=geo_df.geometry.x, 
                        hover_name="title", hover_data=["artist_name", "art_type", "neighborhood"],# identifies columns that should be displayed in the result
                        color_discrete_sequence=["fuchsia"], zoom=10)
        fig.update_layout(mapbox_style="open-street-map")
        fig.show()
    elif y=='3': 
        result = art_database[art_database['title'] == x]
        
        # generating output on an interactive map of all art locations by the art installations tahe user identifies by name
        crs = ('epsg:4326') # defining coordinate projection system 
        geometry = [Point(xy) for xy in zip(result['longitude'], result['latitude'])]
        geo_df = gpd.GeoDataFrame(result, crs = crs, geometry = geometry)
        fig = px.scatter_mapbox(geo_df, lat=geo_df.geometry.y, lon=geo_df.geometry.x, 
                        hover_name="title", hover_data=["artist_name", "art_type", "neighborhood"],# identifies columns that should be displayed in the result
                        color_discrete_sequence=["fuchsia"], zoom=10)
        fig.update_layout(mapbox_style="open-street-map")
        fig.show()


def art_query(art_database): # function to work on the art database
    ''' 
    PURPOSE: To request user input and return results
    
    INPUTS: output from get_art_data()
    
    OUTPUT: Returns an interactive map of art installations, and includes details on the artwork, the artist, and the neighborhood. 
    '''
  
    # imports
    import plotly.express as px
    import plotly.io as pio
    pio.renderers.default='browser' 
    
    import pandas as pd
    import geopandas as gpd
    from shapely.geometry import Point

    
    ex=1# creates a variable ex to create a while loop so that once user has completed search or put in wrong criteria the loop restarts
    while (ex!=0):#while loop allows the user to restart search if wrong criteria entered or result has been found
        print("Please enter the the category number to search by")#creating user interface, asking for search categories
        print("1. Name of Neighbourhood")
        print("2. Name of Artist ")
        print("3. Name of Art Installation")
        print("4. Show all art installations")
        print("0. To exit the search ")
        num=input("Input the required number field: ")
        if (num=='1'):
            neighbourhood=input("Enter neighbourhood: ")#creates if condition to check if searched neighbourhood is in the database
            neighbourhood = neighbourhood.title()
            art_search(neighbourhood,num, art_database)
        elif(num=='2'):
            artist_name = input("Enter Artist Name: ")#creates if condition to check if searched artist name is in the database
            artist_name = artist_name.title()
            art_search(artist_name,num, art_database)
        elif(num=='3'):
            art_title = input("Enter name of art exhibition: ")#creates if condition to check if searched art exhibition is in the database
            art_title = art_title.title()
            art_search(art_title,num, art_database)
        elif(num=='4'):
            result = art_database[art_database['latitude'] != "Not Available"]#creates if condition to display all art installations if the user has no search criteria
            # generating output
            crs = ('epsg:4326') # defining coordinate projection system 
            geometry = [Point(xy) for xy in zip(result['longitude'], result['latitude'])]
            geo_df = gpd.GeoDataFrame(result, crs = crs, geometry = geometry)
            fig = px.scatter_mapbox(geo_df, lat=geo_df.geometry.y, lon=geo_df.geometry.x, 
                            hover_name="title", hover_data=["artist_name", "art_type", "neighborhood"],
                            color_discrete_sequence=["fuchsia"], zoom=10)
            fig.update_layout(mapbox_style="open-street-map")
            fig.show()

        elif(num=='0'):
            ex=(int)(num)
        else:
            print("Choose 1,2, 3, or 4 only")# else condition suggesting to put the correct option number
    
        
######## Helper functions for event query
# Extract and create event dataset
def get_event_data():
    ''' 
    PURPOSE: Web scrapes event data from Downtown Pittsburgh website, and creates a clean dataset of events and their date/times 
    
    INPUTS: takes no input
    
    OUTPUT: A clean dataset of events and their date/times 
    '''
    # import packages
    import requests
    from bs4 import BeautifulSoup
    import pandas as pd
    import datetime as dt
    
    # start webscraping: using url, extract HTML code, and parse to extract data of interest
    url = "https://downtownpittsburgh.com/events/"
    page = requests.get(url)
    page.status_code # should be 200, if not, check url 
    page_html = BeautifulSoup(page.content, 'html.parser')
    
    # Parse HTML: find all events using class = eventitem 
    events_all = page_html.find_all(class_ = "eventitem")
    
    # initialize final dataframe 
    events_data = pd.DataFrame(columns = ['EventName', 'Category', 'startDate','endDate','Time'])
    for event in events_all:
        extracolumn = []
        
        # Parse HTML: get event categories (some have one, some have many)
        categories = event.find(class_ = 'category').find_all(class_ = 'term')
        category = []
        for cat in categories: 
            category.append(cat.get_text().strip(','))
    
        # Parse HTML: get event name
        event_name = event.select('a')[0].get_text()
        
        # Parse HTML: get event date and time, if available
        date_time = event.find(class_ = 'eventdate').get_text().strip().replace('\t', '').split('|')
        if len(date_time) == 1: 
            event_date = date_time[0].strip()
            event_time = 'Timings unavailable'
        
        elif len(date_time) == 2: 
            event_date = date_time[0].strip()
            event_time = date_time[1].strip()
        
        # Further split date into startDate and endDate
        extracolumn = event_date.split('-')
        if len(extracolumn) == 1:
            startDate = extracolumn[0]
            endDate = startDate
        elif len(extracolumn) == 2:
            startDate = extracolumn[0]   
            endDate = extracolumn[1]
            
    
        # create data frame
        event_data = pd.DataFrame([[event_name, category, startDate, endDate, event_time]], columns = ['EventName', 'Category', 'startDate','endDate', 'Time'])
        event_data['startDate'] = pd.to_datetime(event_data['startDate'])
        event_data['endDate'] = pd.to_datetime(event_data['endDate'])
        
       
        # concat with larger data frame
        events_data = pd.concat([events_data, event_data], ignore_index = True)
    
    return(events_data)
        
#Helper function for input of the event date, run query 
def events_query(df):
    ''' 
    PURPOSE: Asks the user to input a date based on the given format, and application would print the relevant events occurring on that day
    
    INPUTS: Takes output from get_event_data()
    
    OUTPUT: A table with relevant events occurring on that day
    '''
    
    import plotly.graph_objects as go
    import pandas as pd 
    print('What event are you looking for?')
    #Asks the user to input a date based on the given format
    dateSpecification = input('\n Enter a start date (YYYY-MM-DD) on which you would like to explore events:')
    #if the date is within the particular date range (since some events might last a couple of days) including the start and end date
    #then the application would print the relevant events occurring on that day
    ahead = df.copy()
    ahead = ahead[(ahead.startDate <= dateSpecification) & (ahead.endDate >= dateSpecification)]
    print('\n Events matching search....  \n')
    
    # displaying date as a string
    startDate_str = []
    endDate_str = []
    for i in range(0, len(ahead)):
        startDate_str.append(str(ahead.iloc[i].startDate)[0:10])
        endDate_str.append(str(ahead.iloc[i].endDate)[0:10])
    
    ahead['startDate_str'] = startDate_str
    ahead['endDate_str'] = endDate_str
    
    #The events are sorted by the category of every event which maybe one or more   
    ahead.sort_values(by = 'Category', inplace = True)
    
    #This function is used to display the events table separately in a formatted way for the user to view easily
    #The table header and cells are assigned different colours for better visuals
    fig = go.Figure(data=[go.Table(
    header=dict(values=['EventName', 'Category', 'Start Date', 'End Date', 'Time'],
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[ahead.EventName, ahead.Category, ahead.startDate_str, ahead.endDate_str, ahead.Time],
               fill_color='lavender',
               align='left'))])

    fig.show()
    
    
#### main function call  
def main():
    ex=1
    while ex != 0: 
        print("\nHello! Welcome to Pittsburgh! What are you looking for?")
        print("Please choose one of the options below: ")
        print("Option 1: Search for Restaurants")
        print("Option 2: Search for Art Installations")
        print("Option 3: Search for Events")
        print("0: To exit the search ")
        user_choice = int(input("\nChoose an option: "))
        
        
        if user_choice == 1: 
            res_data = get_restaurant_data()
            restaurant_query(res_data)
            
        elif user_choice == 2: 
            art_data = get_art_data()
            art_query(art_data) 
            
        elif user_choice == 3:         
            events_data = get_event_data()
            events_query(events_data)
        
        elif user_choice == 0: 
            break
            
        while user_choice not in [1,2,3]:
            user_choice = int(input("\nInvalid choice! Please choose again: "))
            if user_choice == 1: 
                res_data = get_restaurant_data()
                restaurant_query(res_data)
                
            elif user_choice == 2: 
                art_data = get_art_data()
                art_query(art_data) 
                
            elif user_choice == 3:         
                events_data = get_event_data()
                events_query(events_data)
            
            if user_choice == 0:
                break 
            
    


# Run application     
if __name__ == '__main__':
    main()   


    
    
    
