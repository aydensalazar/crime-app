from flask import Flask, render_template
import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster
from folium.plugins import HeatMap
import re
import requests

# import crime data
crime = requests.get("https://data.cityofberkeley.info/resource/k2nh-s5h5.json?$limit=50000")
crime = crime.json()
crime = pd.DataFrame.from_dict(crime)

# add coordinates column
crime['Latitude'] = crime['block_location'].apply(lambda x: x.get('latitude'))
crime['Longitude'] = crime['block_location'].apply(lambda x: x.get('longitude'))

crime['Longitude'] = crime['Longitude'].replace(r'\s+', np.nan, regex=True)
crime['Longitude'] = crime['Longitude'].replace(r'^$', np.nan, regex=True)
crime['Longitude'] = crime['Longitude'].fillna(-0.99999)
crime['Longitude'] = pd.to_numeric(crime['Longitude'])
crime['Latitude'] = crime['Latitude'].replace(r'\s+', np.nan, regex=True)
crime['Latitude'] = crime['Latitude'].replace(r'^$', np.nan, regex=True)
crime['Latitude'] = crime['Latitude'].fillna(-0.99999)
crime['Latitude'] = pd.to_numeric(crime['Latitude'])

# check for any NA/null values
#sum(crime['Coordinates'].isna())
crime.isnull().sum()
crime = crime.drop([':@computed_region_b3wi_w8ix',
                    ':@computed_region_fhmw_rucx',
                    ':@computed_region_u3y2_d2ws',
                    ':@computed_region_5s6d_2f32',
                    ':@computed_region_3ini_iehf',
                    ':@computed_region_5bih_7r3y',
                    ':@computed_region_x3q3_gi3e',], axis=1)
# drop null values
crime = crime.dropna()

#Create the Map
map = folium.Map(
    location=[37.871853, -122.258423],
    zoom_start=14.5
)

#Make the list of Latitude/Longitude/Offense
lat = crime['Latitude'].tolist()
lng = crime['Longitude'].tolist()
offense = crime['offense'].tolist()
locations = list(zip(lat, lng))
offense = crime['offense'].tolist()

marker_cluster = MarkerCluster(
    name="Crimes by Marker",
    overlay=True,
    control=True
)

#popup = folium.Popup(iframe,
                     #max_width=100)

#marker = folium.Marker([43.775, 11.254],
                       #popup=popup).add_to(m)

for i in range(len(lat)):
    location = lat[i], lng[i]
    crime_type = offense[i]
    #marker = folium.Marker(location=location)
    html = '''<b> Type of Crime: </b> {}<br>
            Latitude: {}<br>
            Longitude:{}<br>'''.format(crime_type, location[0], location[1])
    iframe = folium.IFrame(html, width=200, height=200)
    popup = folium.Popup(iframe, max_width=200)
    marker = folium.Marker(location= location,popup=popup)
    marker_cluster.add_child(marker)


marker_cluster.add_to(map)

HeatMap(
    data=list(zip(lat, lng)),
    name="Crimes by Heatmap").add_to(map)
folium.LayerControl().add_to(map)

html_map = map._repr_html_()

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", map = html_map)

@app.route("/map/")
def map():
    return render_template("map.html")

@app.route("/avoid/")
def avoid():
    return render_template("avoidance_map.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
