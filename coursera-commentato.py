import json
import folium
import requests
import mimetypes
import http.client
import pandas as pd
from folium.plugins import HeatMap
from pandas.io.json import json_normalize

#accedere ai dati con API al sito indicato tro le virgolette
# prendo il token composto da header e payload per
conn=http.client.HTTPSConnection("api.covid19api.com")
payload=''
headers={}
conn.request('GET','/summary',payload,headers)
res=conn.getresponse()
data=res.read().decode('UTF-8')
#convertire i dati da UTF-8 in json
covid1=json.loads(data)
#normalizzare i dati
pd.json_normalize(covid1['Countries'],sep=",")
#convertire in panda dataframe
df=pd.DataFrame(covid1['Countries'])
#cancellare colonne vuote
covid2=df.drop(columns=['CountryCode','Slug','Date','Premium'],axis=1)
#genero la mappa di base da Folium e la salvo in index.html
m=folium.Map(tiles='Stamen Terrain',min_zoom=1.5)
##ottenere i geodata
url='https://raw.githubusercontent.com/python-visualization/folium/master/examples/data'
country_shapes=f'{url}/world-countries.json'
#generazione mappa choroplet
folium.Choropleth(
    geo_data=country_shapes,
    min_zoom=2,
    name='Covid-19',
    data=covid2,
    columns=['Country','TotalConfirmed'],
    key_on='feature.properties.name',
    fill_color='OrRd',
    nan_fill_color='black',
    legend_name='Total Confirmed Covid Cases',
).add_to(m)
#m.save('index.html')
covid2.update(covid2['TotalConfirmed'].map('TotalConfirmed:{}'.format))
covid2.update(covid2['TotalRecovered'].map('Total Recovered:{}'.format))
coordinates=pd.read_csv('https://raw.githubusercontent.com/VinitaSilaparasetty/covid-map/master/country-coordinates-world.csv')
covid_final=pd.merge(covid2,coordinates,on='Country')
#faccio i cerchietti
def plotDot(point):
    folium.CircleMarker(location=[point.latitude,point.longitude],
        radius=5,
        weight=2,
        popup=[point.Country,point.TotalConfirmed,point.TotalRecovered],
        fill_color='#000000').add_to(m)
covid_final.apply(plotDot,axis=1)
m.fit_bounds(m.get_bounds())
#faccio la HeatMap
mapbw=folium.Map(tiles='StamenToner',min_zoom=2)
deaths=covid_final['TotalDeaths'].astype(float)
lat=covid_final['latitude'].astype(float)
lon=covid_final['longitude'].astype(float)
mapbw.add_child(HeatMap(zip(lat,lon,deaths),radius=0))
mapbw.save('index2.html')
def plotDot(point):
    folium.CircleMarker(location=[point.latitude,point.longitude],
    radius=5,
    weight=2,
    popup=[point.Country,point.TotalDeaths],
    fill_color='#000000').add_to(mapbw)
covid_final.apply(plotDot,axis=1)
mapbw.fit_bounds(mapbw.get_bounds())
mapbw.save('index3.html')    
