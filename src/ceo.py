import streamlit as st
import pandas as pd
import requests
import functions
import datetime


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

    selectedDate = st.date_input("Select a date to view all events on that day:")
    dfSelectedDayEvents = getEventsOnDay(selectedDate)
    st.write(dfSelectedDayEvents[['eventid','location','start_at','end_at','event_name','over_21']].assign(foo="").set_index('foo'))

    st.markdown("Here is the contact information for all event planners on this day:")
    st.write(dfSelectedDayEvents[['eventid','event_name','event_planner_email']].assign(foo="").set_index('foo'))


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


def getEventsOnDay(date: datetime.date):
    qEventsOnDay = "SELECT * \
                    FROM events \
                    WHERE ('"+ str(date) + " 00:00:00-05','"+ str(date) + " 23:59:59-05') \
                        OVERLAPS \
                        (start_at, end_at);"
    return functions.query_db_no_cache(qEventsOnDay)