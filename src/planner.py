import streamlit as st
import functions
import pandas

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
        qFetchEvents = "SELECT * FROM events WHERE event_planner_email LIKE '" + user + \
            "' ORDER BY date, start_at;"
        dfEventsAll = functions.query_db(qFetchEvents)
        
        # Give the user a quick glance of all their created events
        st.markdown("### Events planned by " + userName + ":")
        fmt = "%H:%M:%S"
        dfEventsSurvey = dfEventsAll[['date', 'start_at', 'end_at', 'event_name']]
        st.table(dfEventsSurvey)

        # For each event, display the location details
        st.markdown('### Locations for all events:')
        st.markdown('### REQUIRES THAT BOOKINGS BE COMPLETED')
        qEventLocations = "SELECT E.date, E.start_at, E.end_at, V.address, V.roomNum FROM events E, resources_venues V WHERE E.location like V.address ORDER BY E.date, E.start_at;"
        dfEventLocations = functions.query_db(qEventLocations)
        st.table(dfEventLocations)

    elif(action == "Book Resources"):
        pass
    elif(action == "Cancel an Event"):
        pass
    
