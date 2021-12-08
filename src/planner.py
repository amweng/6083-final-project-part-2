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

    aEventPlannerActions = ["Make a New Event", "View Your Events", "Book Resources", "Cancel Resource Booking", "Cancel an Event"]
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
        st.markdown("# Make a Booking")
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

        # Get the list of all resources already booked for this event
        qBookedResources = "SELECT B.description, B.resourcetype, B.cost, B.start_at, B.end_at FROM bookings B WHERE eventid = " + str(dfSelectedEvent['eventid'][0]) + ";"
        dfBookedResources = pandas.DataFrame(columns=['description', 'resourcetype', 'cost', 'start_at', 'end_at'])
        dfBookedResources = dfBookedResources.append(functions.query_db_no_cache(qBookedResources))

        st.markdown("### List of current bookings for this event:")
        if st.button("Refresh List"):
            st.dataframe(dfBookedResources)
        else:
            st.dataframe(dfBookedResources)


        
        # Get list of all bookable resources
        qBookableResources = "SELECT pg_type.typname, pg_enum.enumlabel FROM pg_enum, pg_type \
                             WHERE pg_type.oid = pg_enum.enumtypid AND pg_type.typname like 'resourcetype' \
                             ORDER BY pg_enum.enumlabel; "
        dfBookableResources = functions.query_db(qBookableResources)

        selectedResourceType = st.selectbox('Select a type of resource for which you would like to make a booking:', dfBookableResources['enumlabel'])
        
        ## Here is a list of available resources of that type
        dfAllAvailable = bookings.getAllAvailable(dfSelectedEvent['eventid'][0],selectedResourceType, dfSelectedEvent)
        
        if(selectedResourceType == 'Caterer'):
            dfAllAvailableDisplay = dfAllAvailable[['name', 'fee']]
            st.markdown('#### Here is a list of all available caterers for your event:')
            st.table(dfAllAvailableDisplay)
            
            # Selection box for caterers
            aAvailableID = dfAllAvailable['name'].tolist()
            aAvailableKey = dfAllAvailable['typeid'].tolist()
            dicAvailable = dict(zip(aAvailableKey, aAvailableID))
            selectedResource = st.selectbox('Select a caterer you would like to book:', aAvailableKey, format_func= lambda x: dicAvailable[x])
            
            # Get selected resource details in case of booking
            qSelectedResourceDetails = "SELECT * FROM resources_caterers R WHERE R.typeid = " + str(selectedResource) + ";"
            dfSelectedResourceDetails = functions.query_db(qSelectedResourceDetails)

            st.write(dfSelectedResourceDetails)

            st.markdown("##### Would you like to book this resource?")
            if st.button('Reserve this Resource!'):
                bookings.makeBooking(dfSelectedEvent, dfSelectedResourceDetails, 1)
                st.markdown('Resource Booked!')


        elif(selectedResourceType == 'Entertainment'):
            dfAllAvailableDisplay = dfAllAvailable[['name', 'genre', 'contentrating', 'fee']]
            st.markdown('#### Here is a list of all available enteratiners for your event:')
            st.markdown('Please note, this list represents only those entertainers whose act has been specified to fit within the stage space of your specifed venue.' +
                        ' Not all entertainers have specified such a requirement.  You are encouraged to contact them or a customer service representative to confirm that ' +
                        'their act will fit in your space.')
            st.table(dfAllAvailableDisplay)
            
            # Selection box for entertainers
            aAvailableID = dfAllAvailable['name'].tolist()
            aAvailableKey = dfAllAvailable['typeid'].tolist()
            dicAvailable = dict(zip(aAvailableKey, aAvailableID))
            selectedResource = st.selectbox('Select a caterer you would like to book:', aAvailableKey, format_func= lambda x: dicAvailable[x])
            
            # Get selected resource details in case of booking
            qSelectedResourceDetails = "SELECT * FROM resources_entertainment R WHERE R.typeid = " + str(selectedResource) + ";"
            dfSelectedResourceDetails = functions.query_db(qSelectedResourceDetails)

            st.write(dfSelectedResourceDetails)

            st.markdown("##### Would you like to book this resource?")
            if st.button('Reserve this Resource!'):
                bookings.makeBooking(dfSelectedEvent, dfSelectedResourceDetails, 1)
                st.markdown('Resource Booked!')

        elif(selectedResourceType == 'Equipment'):
            dfAllAvailableDisplay = dfAllAvailable[['name', 'equipmenttype', 'quantity', 'fee']]
            st.markdown('#### Here is a list of all available equipment for your event:')
            st.table(dfAllAvailableDisplay)

            # Selection box for entertainers
            aAvailableID = dfAllAvailable['name'].tolist()
            aAvailableKey = dfAllAvailable['typeid'].tolist()
            dicAvailable = dict(zip(aAvailableKey, aAvailableID))
            selectedResource = st.selectbox('Select a piece of equipment you would like to book:', aAvailableKey, format_func= lambda x: dicAvailable[x])
            
            # Get selected resource details in case of booking
            qSelectedResourceDetails = "SELECT * FROM resources_equipment R WHERE R.typeid = " + str(selectedResource) + ";"
            dfSelectedResourceDetails = functions.query_db(qSelectedResourceDetails)

            st.write(dfSelectedResourceDetails)

            st.markdown("Booking this resource will require the following additional bookings: ")
            dfSelectedEquipmentRequirements = bookings.getRequiredResources(str(dfSelectedResourceDetails['resourcetype'][0]), str(dfSelectedResourceDetails['typeid'][0]))
            st.write(dfSelectedEquipmentRequirements[['item', 'requires', 'fee']])

            st.markdown("##### Would you like to book this resource?")
            if st.button('Reserve this Resource!'):
                bookings.makeBooking(dfSelectedEvent, dfSelectedResourceDetails, 1)
                st.markdown('Resource Booked!')

        elif(selectedResourceType == 'Staff'):
            qQualificationsAvailable = "SELECT pg_enum.enumlabel FROM pg_enum, pg_type \
                             WHERE pg_type.oid = pg_enum.enumtypid AND pg_type.typname like 'qualification' \
                             ORDER BY pg_enum.enumlabel; "
            dfQualificationsAvailable = functions.query_db(qQualificationsAvailable)
            dfQualificationsAvailable.at[5,:] = 'None (ie, General Labourer)'
            selectedQualification = st.selectbox('Which qualification does the staffperson require?', dfQualificationsAvailable['enumlabel'])

            dfQualifiedStaff = bookings.isStaffAvailableQualified(selectedQualification, dfSelectedEvent)
            
            st.markdown("Here is a list of qualified, available staff for your event:")
            dfQualifiedStaffDisplay = dfQualifiedStaff[['first_name', 'last_name', 'qualification', 'fee']]
            st.write(dfQualifiedStaffDisplay)
        elif(selectedResourceType == 'Venue'):
            # An event can only have one venue, therefore this option serves the let the user switch venues rather than book more!
            qExistingEventLocation = "SELECT V.name FROM events E, resources_venues V " + \
                                     "WHERE eventid = " + str(dfSelectedEvent['eventid'][0]) + \
                                     "AND E.location = V.address;"
            dfExistingEventLocation = functions.query_db_no_cache(qExistingEventLocation)
            st.markdown("### ATTENTION: You can only have one venue for your event!")
            st.markdown("> Your event is currently taking place at the venue '" + str(dfExistingEventLocation['name'][0]) + "'.  If you book a new venue, it will replace this venue!")
            
            if(dfAllAvailable.size == 0):
                st.markdown("## NO VENUES FOUND!")
                st.markdown("**Given the size of your event, or space required by your entertainers, there are no alternative venues in our database for your event. " + 
                            "If you desire to rebook your venue, please consider downsizing the size of your event.**")
                st.markdown("#### Attention: univiting guests may have unintended consequences!")
            else:
                dfAllAvailableDisplay = dfAllAvailable[['name', 'address', 'roomnum', 'capacity', 'liquorlicense', 'stagearea', 'fee']]

            
                st.markdown('#### Here is a list of alternative venues for your event:')
                st.table(dfAllAvailableDisplay)

                # Selection box for venues
                aAvailableID = dfAllAvailable['name'].tolist()
                aAvailableKey = dfAllAvailable['typeid'].tolist()
                dicAvailable = dict(zip(aAvailableKey, aAvailableID))
                selectedResource = st.selectbox('Select a new venue you would like to book:', aAvailableKey, format_func= lambda x: dicAvailable[x])
                
                # Get selected resource details in case of booking
                qSelectedResourceDetails = "SELECT * FROM resources_venues R WHERE R.typeid = " + str(selectedResource) + ";"
                dfSelectedResourceDetails = functions.query_db(qSelectedResourceDetails)

                st.write(dfSelectedResourceDetails)

                st.markdown("##### Would you like to book this resource?")
                if st.button('Reserve this Resource!'):
                    bookings.makeBooking(dfSelectedEvent, dfSelectedResourceDetails, 1)
                    st.markdown('Resource Booked!')
        else:
            "Something has gone horribly wrong and I'll probably die!"

    elif(action == "Cancel Resource Booking"):
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
        
        # Get the list of all resources already booked for this event
        qBookedResources = "SELECT B.description, B.resourcetype, B.typeid, B.cost, B.start_at, B.end_at FROM bookings B WHERE eventid = " + str(dfSelectedEvent['eventid'][0]) + ";"
        dfBookedResources = pandas.DataFrame(columns=['description', 'resourcetype', 'cost', 'start_at', 'end_at'])
        dfBookedResources = dfBookedResources.append(functions.query_db_no_cache(qBookedResources))

        st.markdown("### List of current bookings for this event:")
        if st.button("Refresh List"):
            st.dataframe(dfBookedResources)
        else:
            st.dataframe(dfBookedResources)

        st.markdown("# Got to here and had to stop for the night.  Smoother to select type to cancel, then query up list, then select.")
        aBookedResourceSelectName = dfBookedResources['description'].tolist()
        aBookedResourceSelectID = dfBookedResources['typeid'].tolist()
        aBookedResourceSelectType = dfBookedResources['resourcetype'].tolist()
        dictBookedResourceSelect = dict(zip(zip(aBok)))
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
    
