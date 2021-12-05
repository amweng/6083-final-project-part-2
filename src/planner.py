import streamlit as st
import functions
import pandas
import datetime
import pytz
import tzlocal
import bookings

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
        # Find all events possessed by the selected user
        qFetchEvents = "SELECT * FROM events E WHERE E.event_planner_email LIKE '" + user + \
            "' ORDER BY date, start_at;"
        dfEventsAll = functions.query_db(qFetchEvents)
        
        # Give the user a quick glance of all their created events
        st.markdown("### All events planned by " + userName + ":")
        dfEventsSurvey = dfEventsAll[['date', 'start_at', 'end_at', 'event_name']]
        for idx in range(len(dfEventsSurvey['start_at'])):
            dfEventsSurvey['start_at'][idx] = functions.pd_timestamp_to_dt_with_tz(dfEventsSurvey['start_at'][idx])
            dfEventsSurvey['end_at'][idx] = dfEventsSurvey['end_at'][idx].isoformat()
        st.table(dfEventsSurvey)

        # EVENT SELECT BOX
        # fetch the list of all events
        qFetchEvents = "SELECT * FROM events E WHERE E.event_planner_email LIKE '" + user + \
            "' ORDER BY date, start_at;"
        dfEventsAll = functions.query_db(qFetchEvents)

        if(dfEventsAll.empty):
            st.markdown("Hello, new user!  Select 'Make an Event' to create a new event!")

        # create a callable dictionary of name:id pairs for the select box
        dfEventSelect = dfEventsAll[['event_name', 'eventid']]
        aEventSelectName = dfEventSelect['event_name'].tolist()
        aEventSelectID = dfEventSelect['eventid'].tolist()
        dic = dict(zip(aEventSelectID, aEventSelectName))
        selectedEvent = st.selectbox('Select an event for which you would like to view the details:', aEventSelectID, format_func=lambda x: dic[x])

        # use the selected event to extract the event row for the selected event
        qSelectedDetails = "SELECT * FROM events E WHERE E.event_planner_email LIKE '" + user + \
                            "' AND eventid = " + str(selectedEvent) + " ORDER BY date, start_at;"
        dfSelectedEvent = functions.query_db(qSelectedDetails)

        # For each event, display the location details
        st.markdown('### Locations for all events:')
        st.markdown('### REQUIRES THAT BOOKINGS BE COMPLETED')
        qEventLocations = "SELECT E.date, E.start_at, E.end_at, V.address, V.roomNum FROM events E, resources_venues V WHERE E.location like V.address ORDER BY E.date, E.start_at;"
        dfEventLocations = functions.query_db(qEventLocations)
        st.table(dfEventLocations)

    elif(action == "Book Resources"):
        # EVENT SELECT BOX
        # fetch the list of all events
        qFetchEvents = "SELECT * FROM events E WHERE E.event_planner_email LIKE '" + user + \
            "' ORDER BY date, start_at;"
        dfEventsAll = functions.query_db(qFetchEvents)

        if(dfEventsAll.empty):
            st.markdown("Hello, new user!  Select 'Make an Event' to create a new event!")

        # create a callable dictionary of name:id pairs for the select box
        dfEventSelect = dfEventsAll[['event_name', 'eventid']]
        aEventSelectName = dfEventSelect['event_name'].tolist()
        aEventSelectID = dfEventSelect['eventid'].tolist()
        dic = dict(zip(aEventSelectID, aEventSelectName))
        selectedEvent = st.selectbox('Select an event for which you would like to make a booking:', aEventSelectID, format_func=lambda x: dic[x])

        # use the selected event to extract the event row for the selected event
        qSelectedDetails = "SELECT * FROM events E WHERE E.event_planner_email LIKE '" + user + \
                            "' AND eventid = " + str(selectedEvent) + " ORDER BY date, start_at;"
        dfSelectedEvent = functions.query_db(qSelectedDetails)
        
        # Get list of all bookable resources
        qBookableResources = "SELECT pg_type.typname, pg_enum.enumlabel FROM pg_enum, pg_type \
                             WHERE pg_type.oid = pg_enum.enumtypid AND pg_type.typname like 'resourcetype' \
                             ORDER BY pg_enum.enumlabel; "
        dfBookableResources = functions.query_db(qBookableResources)

        selectedResourceType = st.selectbox('Select a type of resource for which you would like to make a booking:', dfBookableResources['enumlabel'])
        
        ## Here is a list of available resources of that type
        dfAllAvailable = bookings.getAllAvailable(selectedResourceType, dfSelectedEvent)
        
        if(selectedResourceType == 'Caterer'):
            dfAllAvailableDisplay = dfAllAvailable[['name', 'fee']]
            st.markdown('#### Here is a list of all available caterers for your event:')
            st.table(dfAllAvailableDisplay)
        elif(selectedResourceType == 'Entertainment'):
            dfAllAvailableDisplay = dfAllAvailable[['name', 'genre', 'contentrating', 'fee']]
            st.markdown('#### Here is a list of all available enteratiners for your event:')
            st.table(dfAllAvailableDisplay)
        elif(selectedResourceType == 'Equipment'):
            dfAllAvailableDisplay = dfAllAvailable[['name', 'equipmenttype', 'quantity', 'fee']]
            st.markdown('#### Here is a list of all available equipment for your event:')
            st.table(dfAllAvailableDisplay)
        elif(selectedResourceType == 'Staff'):
            st.markdown('### PUT A SELECT BOX FOR STAFF QUALIFICATIONS')
        elif(selectedResourceType == 'Venue'):
            dfAllAvailableDisplay = dfAllAvailable[['name', 'address', 'roomnum', 'capacity', 'liquorlicense', 'stagearea', 'fee']]
            st.markdown('#### Here is a list of all available venues for your event:')
            st.table(dfAllAvailableDisplay)
        else:
            "Something has gone horribly wrong and I'll probably die!"
        

    elif(action == "Cancel an Event"):
        # fetch the list of all events
        qFetchEvents = "SELECT * FROM events E WHERE E.event_planner_email LIKE '" + user + \
            "' ORDER BY date, start_at;"
        dfEventsAll = functions.query_db(qFetchEvents)

        if(dfEventsAll.empty):
            st.markdown("Hello, new user!  Select 'Make an Event' to create a new event!")

        # create a callable dictionary of name:id pairs for the select box
        dfEventSelect = dfEventsAll[['event_name', 'eventid']]
        aEventSelectName = dfEventSelect['event_name'].tolist()
        aEventSelectID = dfEventSelect['eventid'].tolist()
        dic = dict(zip(aEventSelectID, aEventSelectName))
        selectedEvent = st.selectbox('Select an event you would like to cancel:', aEventSelectID, format_func=lambda x: dic[x])

        # use the selected event to extract the event row for the selected event
        qSelectedDetails = "SELECT * FROM events E WHERE E.event_planner_email LIKE '" + user + \
                            "' AND eventid = " + str(selectedEvent) + " ORDER BY date, start_at;"
        dfSelectedEvent = functions.query_db(qSelectedDetails)
        pass
    
