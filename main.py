# -*- coding: utf-8 -*-
"""CoronaTracker_SQL.ipynb

Automatically generated by Colaboratory.

"""

import sqlalchemy as db
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go

import os

def generate_geomap():
    """Using SQLAlchemy"""

    engine = db.create_engine('mysql+mysqlconnector://' + os.environ.get('SQL_USER') + ':' + os.environ.get('SQL_PW') + '@coronatracker.coehycitad7u.ap-southeast-1.rds.amazonaws.com/coronatracker')
    connection = engine.connect()
    metadata = db.MetaData()
    print(metadata.tables)

    ## executing the statement using 'execute()' method
    query = engine.execute("SHOW DATABASES")

    ## 'fetchall()' method fetches all the rows from the last executed statement
    databases = query.fetchall() ## it returns a list of all databases present

    ## printing the list of databases
    print(databases)

    ## executing the statement using 'execute()' method
    query = engine.execute("SHOW TABLES FROM coronatracker")

    ## 'fetchall()' method fetches all the rows from the last executed statement
    tables_coronatracker = query.fetchall() ## it returns a list of all databases present

    print('tables_coronatracker')
    for table in tables_coronatracker:
        print(table)

    ## executing the statement using 'execute()' method
    query = engine.execute("SHOW TABLES FROM information_schema")

    ## 'fetchall()' method fetches all the rows from the last executed statement
    tables_infoschema = query.fetchall() ## it returns a list of all databases present

    print('tables_infoschema')
    for table in tables_infoschema:
        print(table)


    # Corona Tracker Master Table with data from arcgis
    with engine.connect() as conn, conn.begin():
        data = pd.read_sql('SELECT * FROM arcgis', conn, parse_dates=['last_update', 'posted_date'])


    data.rename(columns={'lat': 'latitude', 'lng': 'longitude'}, inplace=True)


    data['coordinates'] = data[['longitude', 'latitude']].values.tolist()


    data['coordinates'] = data['coordinates'].apply(Point)


    data = gpd.GeoDataFrame(data, geometry='coordinates')



    data['deaths'] = data['deaths'].fillna(value=0)
    data['confirmed'] = data['confirmed'].fillna(value=0)
    data['recovered'] = data['recovered'].fillna(value=0)



    data_localized = data.set_index('posted_date').tz_localize(tz='GMT').reset_index()

    data_localized



    data_localized['state'] = data_localized['state'].fillna(value='')
    data_localized['Location Name'] = data_localized['state'] + ', ' + data_localized['country']
    latest_time = data_localized['posted_date'].max()

    data_latest = data_localized[data_localized.posted_date == latest_time]
    fig = px.scatter_geo(data_latest, lat='latitude', lon='longitude',
                        color='deaths',
                        color_continuous_scale='portland',
                        size="confirmed", # size of markers, "Confirmed" is one of the columns of gapminder
                        size_max=80,
                        hover_name='Location Name',
                        title={
                            'text': f'2019-nCoV Confirmed Cases and Deaths as of \
{latest_time.strftime("%d %B %Y %I:%M %p %Z")}',
                            'y': 0.9,
                            'x': 0.5,
                            'xanchor': 'center',
                            'yanchor': 'top',
                            'font': {
                                'size': 16
                                },
                        }
                        )

    fig.update_geos(
        resolution=50,
        showcountries=True, countrycolor="RebeccaPurple"
    )

    fig.update_layout(annotations=[
            go.layout.Annotation(
                x=1.0,
                y=-0.15,
                showarrow=False,
                text="Geomap by: @hweecat",
                xref="paper",
                yref="paper"
            ),
            go.layout.Annotation(
                x=0,
                y=-0.15,
                showarrow=False,
                text="Data: Johns Hopkins University",
                xref="paper",
                yref="paper"
            ),
        ])

    fig.write_html('index.html', config={
        'responsive': True
    })


    os.chdir('archives')
    os.mkdir(latest_time.strftime("%Y%m%d_%H%M"))
    os.chdir(latest_time.strftime("%Y%m%d_%H%M"))

    fig.write_html('index.html', config={
        'responsive': True
    })

    os.chdir('..')
    os.chdir('..')

if __name__ == "__main__":
    generate_geomap()