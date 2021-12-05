import streamlit as st
import functions
import pandas
import datetime
import pytz
import tzlocal

user = 'test'
action = 'test'
userName = 'test'

def getUserID(userName: str, users: pandas.DataFrame):
    dfUserRow = users[users.name.isin([userName])]
    aUserEmail = dfUserRow['email'].tolist()[0]
    return aUserEmail

def getUserName(userEmail: str, users: pandas.DataFrame):
    dfUserRow = user[user.email.isin([userEmail])]
    aUserName = dfUserRow['name'].tolist()[0]
    return aUserName

def pd_timestamp_to_dt_with_tz(pd_ts):
    dt = pd_ts.to_pydatetime()
    ttz = dt.astimezone(datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo)
    timetz = ttz.strftime('%m-%d-%Y %H:%M:%S%z')
    return str(timetz)

def show():
    qEventPlanners = "SELECT email, first_name, last_name FROM event_planners;"
    dfEventPlannerNames = functions.query_db(qEventPlanners)
    dfEventPlannerNames['name'] = (dfEventPlannerNames['first_name'] \
        + ' ' + dfEventPlannerNames['last_name'] + " (" + dfEventPlannerNames['email'] + ')')
    aEventPlannerNames = dfEventPlannerNames['name'].tolist()
    user = st.sidebar.selectbox("Who are you?", aEventPlannerNames)
    userName = user

    aEventPlannerActions = ["Make a New Event", "View Your Events", "Book Resources", "Cancel an Event"]
    action = st.sidebar.selectbox("What do you want to do?", aEventPlannerActions)

    user = getUserID(user, dfEventPlannerNames)

    if(action == "Make a New Event"):
        pass
    elif(action == "View Your Events"):
        qFetchEvents = "SELECT * FROM events E WHERE E.event_planner_email LIKE '" + user + \
            "' ORDER BY date, start_at;"
        dfEventsAll = functions.query_db(qFetchEvents)
        
        # Give the user a quick glance of all their created events
        st.markdown("### Events planned by " + userName + ":")
        dfEventsSurvey = dfEventsAll[['date', 'start_at', 'end_at', 'event_name']]
        for idx in range(len(dfEventsSurvey['start_at'])):
            st.write(dfEventsSurvey['start_at'][idx])
            dfEventsSurvey['start_at'][idx] = pd_timestamp_to_dt_with_tz(dfEventsSurvey['start_at'][idx])
            st.table(dfEventsSurvey)

        # For each event, display the location details
        st.markdown('### Locations for all events:')
        st.markdown('### REQUIRES THAT BOOKINGS BE COMPLETED')
        qEventLocations = "SELECT E.date, E.start_at, E.end_at, V.address, V.roomNum FROM events E, resources_venues V WHERE E.location like V.address ORDER BY E.date, E.start_at;"
        dfEventLocations = functions.query_db(qEventLocations)
        st.table(dfEventLocations)

    elif(action == "Book Resources"):
        qFetchEvents = "SELECT * FROM events E WHERE E.event_planner_email LIKE '" + user + \
            "' ORDER BY date, start_at;"
        dfEventsAll = functions.query_db(qFetchEvents)
        dfEventSelect = dfEventsAll['date'] + dfEventsAll['event_name']
        aEventSelect = []
        for idx in range(len(dfEventsSelect['date'])):
            aEventSelect.append(dfEventSelect['date'][idx].isoformat() + ' -- ' + dfEventSelect['event_name'][idx])

        selectedEvent = st.selectbox('Select an event for which you would like to make a booking:', aEventSelect)

        qSelectedDetails = "SELECT * FROM events E WHERE E.event_planner_email LIKE '" + user + \
                           "' AND ORDER BY date, start_at;"
    elif(action == "Cancel an Event"):
        pass
    
