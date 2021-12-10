import streamlit as st
import pandas as pd
import requests
import functions


def show():
    st.write("# Here's what's happening.")

    q_event_count = "SELECT COUNT(*) from events;"
    df_count = functions.query_db(q_event_count)
    count = df_count.get('count')[0]

    config = functions.get_config(section="mapbox")
    token = str(config['token'])
    coords = getCoordsOfAllEvents(token)

    st.write("### {0} Events at {1} venues on the calendar".format(count, len(coords)))
    st.map(coords, zoom=None)


@st.cache(allow_output_mutation = True)
def getCoordsOfAllEvents(token: str):
    q_locations = "SELECT DISTINCT location from events;"
    addresses = functions.query_db(q_locations)["location"].tolist()
    base_path = "https://api.mapbox.com"
    endpoint = "mapbox.places"
    coords = []
    for address in addresses:
        url = "{0}/geocoding/v5/{1}/{2}.json?access_token={3}".format(base_path, endpoint, address, token)
        r = requests.get(url=url)
        data = r.json()
        xy = data['features'][0]['geometry']['coordinates']
        coords.append(xy)
    return pd.DataFrame(coords, columns=['lon', 'lat'])