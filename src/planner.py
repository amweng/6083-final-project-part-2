import streamlit as st
import functions
import pandas
import matplotlib.pyplot as plt
import datetime
import pytz
import tzlocal
import bookings
import requests


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

def createUser(first: str, last: str, email: str, phone: str, pronoun: str):
            qInsertUser = "INSERT INTO event_planners VALUES (\
                           '" + first + "', \
                           '" + last + "', \
                           '" + email + "', \
                           '" + phone + "', \
                           '" + pronoun + "' \
                          );"
            functions.execute_db(qInsertUser)

def createNewEvent(date: str, start_at: str, end_at: str, location: str, budget: str, email:str, event_name: str, ageQual: str):
            qInsertEvent = "INSERT INTO events VALUES ( nextval('custom_events'), \
                           '" + date + "', \
                           '"+ start_at + "', \
                           '" + end_at + "', \
                           '" + location + "', \
                           '" + budget + "', \
                           '" + email + "', \
                           '" + event_name + "', \
                           '" + ageQual + "');"
            functions.execute_db(qInsertEvent)


@st.cache(allow_output_mutation = True)
def getCoordsOfThisEvent(dfEvent: pandas.DataFrame, token: str):
    # All credit goes to Andrew for figuring this one out!

    address = dfEvent["location"].tolist()
    base_path = "https://api.mapbox.com"
    endpoint = "mapbox.places"
    coords = []
    url = "{0}/geocoding/v5/{1}/{2}.json?access_token={3}".format(base_path, endpoint, address, token)
    r = requests.get(url=url)
    data = r.json()
    xy = data['features'][0]['geometry']['coordinates']
    coords.append(xy)
    return pandas.DataFrame(coords, columns=['lon', 'lat'])

def show():
    qEventPlanners = "SELECT email, first_name, last_name FROM event_planners;"
    dfEventPlannerNames = functions.query_db_no_cache(qEventPlanners)
    dfEventPlannerNames['name'] = (dfEventPlannerNames['first_name'] \
        + ' ' + dfEventPlannerNames['last_name'] + " (" + dfEventPlannerNames['email'] + ')')
    aEventPlannerNames = dfEventPlannerNames['name'].tolist()
    user = st.sidebar.selectbox("Who are you?", aEventPlannerNames)
    userName = user

    aEventPlannerActions = ["Create a New User","Make a New Event", "View Your Events", "Book Resources", "Cancel Resource Booking", "Cancel an Event"]
    action = st.sidebar.selectbox("What do you want to do?", aEventPlannerActions)

    user = getUserID(user, dfEventPlannerNames)

    if(action == "Create a New User"):
        st.markdown("### User Creation Tool")
        st.markdown("All of the following fields are **required**.")
        aFirstName = st.text_input("First Name:")
        aLastName = st.text_input("Last Name:")
        aEmail = st.text_input("Your E-Mail Address:")
        aPhone = st.text_input("Your Contact Number:")
        aPronoun = st.selectbox("Your Preferred Pronouns:",["She / Her", "He / Him", "They, Them", "Please Ask Directly", "Decline To Answer"])

        if(st.button("Create New User")):
            try:
                createUser(aFirstName,aLastName,aEmail,aPhone,aPronoun)
                st.markdown('User Created.')
                st.markdown("You may need to refresh the page in order for them to show up in the selection box at left.")
            except:
                st.markdown("It looks like something wasn't quite right with your input.  Check your responses and try again.")

    elif(action == "Make a New Event"):
        st.markdown(" #### Your currently booked events: ")

        # Find all events possessed by the selected user
        qFetchEvents = "SELECT * FROM events E WHERE E.event_planner_email LIKE '" + user + \
            "' ORDER BY date, start_at;"
        dfEventsAll = functions.query_db_no_cache(qFetchEvents)
        
        # Give the user a quick glance of all their created events
        dfEventsSurvey = dfEventsAll[['date', 'start_at', 'end_at', 'event_name']]
        for idx in range(len(dfEventsSurvey['start_at'])):
            dfEventsSurvey['start_at'][idx] = functions.pd_timestamp_to_dt_with_tz(dfEventsSurvey['start_at'][idx])
            dfEventsSurvey['end_at'][idx] = dfEventsSurvey['end_at'][idx].isoformat()
        st.table(dfEventsSurvey)

        st.markdown("#### Event Information:")
        aEventName = st.text_input('Event Name: ')

        # Event Name
        if(aEventName):
            st.markdown("NB. For the purpose of this exercise, all pre-made events are in the month of December 2021. Custom events can be of any date.")
            aEventDate = st.date_input("Event Date")
            aEventStart = st.time_input("Event Start Time:", value=datetime.time(12,00))
            aEventEnd = st.time_input("Event End Time:", value=datetime.time(13,00))
            
            # MAKE THE DATETIME TIME WINDOW FRAME
            aTZlabels = ['US - Eastern Standard', 'US - Central Standard', 'US - Mountain Standard', 'US - Pacific Standard', 'US - Alaska Standard', 'US - Hawaii-Aleutian Standard']
            aTZvalues = ['-05', '-06', '-07', '-08', '-09', '-10']
            dicTimeZones = dict(zip(aTZvalues, aTZlabels))
            selectedTZ = st.selectbox('Select the timezone for your event:', aTZvalues, format_func= lambda x: dicTimeZones[x])
            
            st.markdown("The option below will set the age limit for your event.  If an event is intended as an adult social event in which alcohol is served, you must mark this as 'True'.")
            aAgeQualifier = st.selectbox("Is this event for adults over 21 years of age only?", ['No', 'Yes'])
            
            # Retrieve all available venues with the timeframe for the event
            dicTimestamps = { 'date':[str(aEventDate)], 
                              'start_at':[str(aEventDate) + ' ' + str(aEventStart) + selectedTZ], \
                              'end_at':[str(aEventDate) + ' ' + str(aEventEnd) + selectedTZ], 
                              'over21':[aAgeQualifier]}
            dfEventTimeframe = pandas.DataFrame(data=dicTimestamps)
            dfAllAvailable = bookings.getAllAvailableVenuesAtTime(dfEventTimeframe)  # Note, presence of a liquor license is folded in to the query if an event is marked as 'over 21' only.
            dfAllAvailableDisplay = dfAllAvailable[['name', 'address', 'roomnum', 'capacity', 'stagearea', 'fee']]
            st.write(dfAllAvailableDisplay)

            # Selection box for venues
            aAvailableID = dfAllAvailable['name'].tolist()
            aAvailableKey = dfAllAvailable['typeid'].tolist()
            dicAvailable = dict(zip(aAvailableKey, aAvailableID))
            selectedResource = st.selectbox('Select a new venue you would like to book:', aAvailableKey, format_func= lambda x: dicAvailable[x])
            
            # Get selected resource details in case of booking
            qSelectedResourceDetails = "SELECT * FROM resources_venues R WHERE R.typeid = " + str(selectedResource) + ";"
            dfSelectedResourceDetails = functions.query_db(qSelectedResourceDetails)

            aEventBudget = st.text_input("What is your estimated budget for this event?")
             

            if(st.button("Create Event")):
                createNewEvent(dfEventTimeframe['date'][0], dfEventTimeframe['start_at'][0], dfEventTimeframe['end_at'][0], \
                                   dfSelectedResourceDetails['address'][0], str(aEventBudget), user, aEventName, dfEventTimeframe['over21'][0])
                try:
                    st.markdown('Event Created!')
                except:
                    st.markdown("Hmmm.... something doesn't seem quite right about your event.  Check the input fields and try again.")



    elif(action == "View Your Events"):
        # Find all events possessed by the selected user
        qFetchEvents = "SELECT * FROM events E WHERE E.event_planner_email LIKE '" + user + \
            "' ORDER BY date, start_at;"
        dfEventsAll = functions.query_db_no_cache(qFetchEvents)
        
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
        dfEventsAll = functions.query_db_no_cache(qFetchEvents)

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
        dfSelectedEvent = functions.query_db_no_cache(qSelectedDetails)

        # For each event, display the location details
        st.markdown("---")
        st.markdown('### Location for this event:')        
        st.markdown("#### " + str(dfSelectedEvent['location'][0]))

        config = functions.get_config(section="mapbox")
        token = str(config['token'])
        coords = getCoordsOfThisEvent(dfSelectedEvent, token)

        st.map(coords,zoom=None)
        st.markdown("---")
        st.markdown("### Schedule of Events: ")
        st.markdown("Your event begins at **" + str(dfSelectedEvent['start_at'][0].astimezone('America/New_York')) + "**")
        st.markdown("Your event ends at **" + str(dfSelectedEvent['end_at'][0].astimezone('America/New_York')) + "**")
        
        st.markdown("---")
        st.markdown("### Catering Reservation")
        qViewCateringReservation = "SELECT C.* \
                                    FROM bookings B, resources_caterers C \
                                    WHERE B.eventid = " + str(dfSelectedEvent['eventid'][0]) + "  \
                                    AND B.resourcetype = 'Caterer' \
                                    AND B.typeid = C.typeid;"
        dfViewCatereringReservation = functions.query_db_no_cache(qViewCateringReservation)

        if(dfViewCatereringReservation.empty):
            st.write("There is no caterer reserved for this event.  Please navigate to the 'Make a Booking' page if you would like to reserve one.")
        else:
            st.write("You have booked **" + dfViewCatereringReservation['name'][0] + "** for your event.")
            st.write("Their per-event fee is ** $" + str(dfViewCatereringReservation['fee'][0]) + "**.")
            st.write("Here is a full list of their available menus:")
            
            qViewCateringMenus = "SELECT MO.name as menu_name, MO.description \
                                 FROM resources_caterers RC, menus_offered MO \
                                 WHERE RC.typeid = " + str(dfViewCatereringReservation['typeid'][0]) + \
                                 "AND RC.name = MO.caterer_name;"
            dfViewCateringMenus = functions.query_db_no_cache(qViewCateringMenus)
            st.write(dfViewCateringMenus.assign(foo="").set_index('foo'))

        st.markdown("---")
        st.markdown("### Entertainment Reservation(s)")

        qViewEntertainmentReservations = "SELECT E.* \
                                        FROM bookings B, resources_entertainment E \
                                        WHERE B.eventid = " + str(dfSelectedEvent['eventid'][0]) + "  \
                                        AND B.resourcetype = 'Entertainment' \
                                        AND B.typeid = E.typeid \
                                        ORDER BY E.name;"
        dfViewEntertainmentReservations = functions.query_db_no_cache(qViewEntertainmentReservations)

        if(dfViewEntertainmentReservations.empty):
            st.write("No entertainers are reserved for this event.  Please navigate to the 'Make a Booking' page if you would like to reserve them.")
        else:
            st.write("Here is the full list of entertainment acts you have booked for your event:")
            st.write(dfViewEntertainmentReservations[['name', 'genre', 'contentrating', 'fee']].assign(foo="").set_index('foo').style.format(subset=['fee'], formatter="{:.2f}"))

        st.markdown("---")
        st.markdown("### Staff Engaged for the Event")
        qViewStaffReservation =  "SELECT S.* \
                                FROM bookings B, resources_staff S \
                                WHERE B.eventid = " + str(dfSelectedEvent['eventid'][0]) + "  \
                                AND B.resourcetype = 'Staff' \
                                AND B.typeid = S.typeid \
                                ORDER BY last_name;"
        dfViewStaffReservation = functions.query_db_no_cache(qViewStaffReservation)

        if(dfViewStaffReservation.empty):
            st.write("No staff members are reserved for this event.  At least one must be engaged as per our terms of service!")
        else:
            st.write("Here is the full list of staff members you have booked for your event:")
            st.write(dfViewStaffReservation[['first_name', 'last_name', 'pronoun','fee']].assign(foo="").set_index('foo').style.format(subset=['fee'], formatter="{:.2f}"))

            st.write("Here are the qualifications for each of your staff members.  Use these to make sure they are assigned to their proper tasks.")
            qViewStaffQualifications =  "SELECT S.*, Q.qualification \
                                FROM bookings B, resources_staff S, qualifications_have Q \
                                WHERE B.eventid = " + str(dfSelectedEvent['eventid'][0]) + "  \
                                AND B.resourcetype = 'Staff' \
                                AND B.typeid = S.typeid \
                                AND S.email = Q.staff_email \
                                ORDER BY last_name;"
            dfViewStaffQualifications = functions.query_db_no_cache(qViewStaffQualifications)
            st.write(dfViewStaffQualifications[['first_name','last_name','qualification']].assign(foo="").set_index('foo'))

        st.markdown("---")
        st.markdown("### Reserved Equipment")
        qViewEquipmentReservation =  "SELECT E.* \
                                FROM bookings B, resources_equipment E \
                                WHERE B.eventid = " + str(dfSelectedEvent['eventid'][0]) + "  \
                                AND B.resourcetype = 'Equipment' \
                                AND B.typeid = E.typeid \
                                ORDER BY name;"
        dfViewEquipmentReservation = functions.query_db_no_cache(qViewEquipmentReservation)

        st.write("Here is a list of all equipment reservations.  Please note that fee is calculated here as per-unit.  See the section below for aggregate cost.")
        st.write(dfViewEquipmentReservation[['name','equipmenttype','quantity','fee']].assign(foo="").set_index('foo').style.format(subset=['fee'], formatter="${:.2f}"))

        st.markdown("---")
        st.markdown("### Finances for this Event")
        qGrossCost = "SELECT sum(cost * num) FROM bookings B WHERE B.eventid = " + str(dfSelectedEvent['eventid'][0]) + ";"
        dfGrossCost = functions.query_db_no_cache(qGrossCost)
        aGrossCost = dfGrossCost['sum'][0]

        if ((dfSelectedEvent['budget'][0] - aGrossCost) > 0.0):
            st.markdown("#### Your event is currently below budget.")
        else:
            st.markdown("#### Your event is currently OVER BUDGET by $" + str(dfSelectedEvent['budget'][0] - aGrossCost))

        st.markdown("Your stated budget for this event was $" + str(dfSelectedEvent['budget'][0]))

        st.markdown("Your current gross cost for the event is $" + str(aGrossCost))

        

        st.markdown("The cost of each of your booking categories is:")
        qItemizedCost = "SELECT A.category, sum, COALESCE(aggregate_cost,0) as itemized_cost, (COALESCE(aggregate_cost,0) / sum) * 100 as percent_cost \
                        FROM ( \
                            SELECT * from ( \
                                SELECT  pg_enum.enumlabel::text as category \
                                    FROM pg_enum, pg_type \
                                    WHERE pg_type.oid = pg_enum.enumtypid \
                                    AND pg_type.typname like 'resourcetype' \
                                    ORDER BY pg_enum.enumlabel ) A, \
                                (SELECT SUM(cost * num)  \
                                FROM bookings \
                                WHERE eventid = " + str(dfSelectedEvent['eventid'][0]) + ") B) A \
                            LEFT JOIN \
                            (SELECT resourcetype::text as category, sum(cost * num) aggregate_cost \
                            FROM 	bookings \
                            WHERE	eventid = " + str(dfSelectedEvent['eventid'][0]) + " \
                            GROUP BY resourcetype) B \
                            ON	A.category = B.category;"
        dfItemizedCost = functions.query_db_no_cache(qItemizedCost)

        # For clean plotting in the pie chart, we remove categories with zero values
        # We need to do this otherwise 
        # keys = dfItemizedCost['category'].tolist()
        # values = dfItemizedCost['percent_cost'].tolist()
        # dictData = dict(zip(keys, values))
        # dictData = {k:v for k,v in dictData.items() if v > 0}
        # labels = list(dictData.keys())
        # values = list(dictData.values())

        fig, ax = plt.subplots()
        ax.pie(dfItemizedCost['percent_cost'].tolist(), labels=dfItemizedCost['category'].tolist())
        ax.axis('equal')
        st.pyplot(fig)
        
        


        



    elif(action == "Book Resources"):
        st.markdown("# Make a Booking")
        # EVENT SELECT BOX
        # fetch the list of all events
        qFetchEvents = "SELECT * FROM events E WHERE E.event_planner_email LIKE '" + user + \
            "' ORDER BY date, start_at;"
        dfEventsAll = functions.query_db_no_cache(qFetchEvents)

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
        dfSelectedEvent = functions.query_db_no_cache(qSelectedDetails)

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
            st.markdown("### Your Guests' Dietary Restrictions")
            st.markdown('The following is a list of all dietary restrictions reported by your guests:')
            dfMenuRequirements = bookings.getAllDietaryRestrictions(dfSelectedEvent)
            st.write(dfMenuRequirements)

            st.markdown("### Accomodating Menus")
            st.markdown('The following is a ranked list of menus provided by the caterers in our database that are specified to accomodate the above restrictions.' +
                        'Please note that accomodation of dietary restrictions is an ad hoc process.  All caterers are capable of accomodating dietary restrictions \
                        to some degree.  However, not all dietary restrictions can be accomodated.  Once you have settled on a caterer you feel bests fits your event\'s \
                        set of restrictions, we encourage you to contact the caterer directly with further questions.')
            dfMenuAccomodations = bookings.getAllAccomodatingMenus(dfSelectedEvent)
            st.write(dfMenuAccomodations)
            
            # Selection box for caterers
            aAvailableID = dfAllAvailable['name'].tolist()
            aAvailableKey = dfAllAvailable['typeid'].tolist()
            dicAvailable = dict(zip(aAvailableKey, aAvailableID))
            selectedResource = st.selectbox('Select a caterer you would like to book:', aAvailableKey, format_func= lambda x: dicAvailable[x])
            
            # Get selected resource details in case of booking
            qSelectedResourceDetails = "SELECT * FROM resources_caterers R WHERE R.typeid = " + str(selectedResource) + ";"
            dfSelectedResourceDetails = functions.query_db(qSelectedResourceDetails)

            st.write(dfSelectedResourceDetails)

            st.markdown('The caterer you have selected offers the following menus which specifically accomodate known restrictions in your guest list: ')
            dfSelectedCatererMenus = bookings.getCaterersAccomodatingMenus(dfSelectedEvent, dfSelectedResourceDetails)
            st.write(dfSelectedCatererMenus)

            st.markdown('Here is a list of all of the caterer\'s menus, along with any restrictions they accomodate:')
            dfAllSelectedCatererMenus = bookings.getAllCatererMenusPlusAccomodations(dfSelectedEvent, dfSelectedResourceDetails)
            st.write(dfAllSelectedCatererMenus)

            st.markdown("Booking this Caterer will automatically create the following additional bookings: ")
            df_vendor_eq_req = bookings.getVendorEquipmentReq(dfSelectedResourceDetails['resourcetype'][0],dfSelectedResourceDetails['typeid'][0])
            st.dataframe(df_vendor_eq_req.style.format(subset=['fee'], formatter="{:.2f}"))


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
            selectedResource = st.selectbox('Select the entertainment you would like to book:', aAvailableKey, format_func= lambda x: dicAvailable[x])
            
            # Get selected resource details in case of booking
            qSelectedResourceDetails = "SELECT * FROM resources_entertainment R WHERE R.typeid = " + str(selectedResource) + ";"
            dfSelectedResourceDetails = functions.query_db(qSelectedResourceDetails)

            st.write(dfSelectedResourceDetails)

            st.markdown("Booking this Entertainer will automatically create the following additional bookings: ")
            df_vendor_eq_req = bookings.getVendorEquipmentReq(dfSelectedResourceDetails['resourcetype'][0],dfSelectedResourceDetails['typeid'][0])
            st.dataframe(df_vendor_eq_req.style.format(subset=['fee'], formatter="{:.2f}"))

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

            # let the user specify a quantity and a descriptioon
            quantity = st.number_input("Quantity", value=0, step=1)

            # Get selected resource details in case of booking
            qSelectedResourceDetails = "SELECT * FROM resources_equipment R WHERE R.typeid = " + str(selectedResource) + ";"
            dfSelectedResourceDetails = functions.query_db(qSelectedResourceDetails)

            st.dataframe(dfSelectedResourceDetails.style.format(subset=['fee'], formatter="{:.2f}"))


            # my implmentation of this function differs slightly in that: If two resources require the same piece
            # of equipment but in differing quantities, we select the line-item requirement that requires a higher
            # quantity and we list that as the reason.
            #
            # Ex: If lighting-set requires 2 power supply and fog machine requires 1, then we list the req. for 2
            # power machines and the specification that lighting-set requires 2 power supply.
            st.markdown("Booking this piece of equipment will automatically create the following additional bookings: ")
            df_vendor_eq_req = bookings.getVendorEquipmentReq(dfSelectedResourceDetails['resourcetype'][0],dfSelectedResourceDetails['typeid'][0])
            st.dataframe(df_vendor_eq_req.style.format(subset=['fee'], formatter="{:.2f}"))

            # st.markdown("Booking this resource will require the following additional bookings: ")
            # dfSelectedEquipmentRequirements = bookings.getRequiredResources(str(dfSelectedResourceDetails['resourcetype'][0]), str(dfSelectedResourceDetails['typeid'][0]))
            # st.write(dfSelectedEquipmentRequirements[['item', 'requires', 'fee']])

            st.markdown("##### Would you like to book this resource?")
            if st.button('Reserve this Resource!'):
                bookings.makeBooking(dfSelectedEvent, dfSelectedResourceDetails, quantity)
                st.markdown('Resource Booked!')

        elif(selectedResourceType == 'Staff'):
            st.markdown('### Staff Requirements for your event:')
            if(bookings.isEvent_Over21(dfSelectedEvent)):
                st.markdown("> You have indicated that the audience for your event be over 21.")
                if(bookings.isBartenderBooked(dfSelectedEvent)):
                    st.markdown("> You **DO** have a bartender booked for this event and **DO NOT** need to book another.")
                else:
                    st.markdown('> YOU DO NOT HAVE A BARTENDER BOOKED FOR THIS EVENT AND MUST BOOK ONE.')

            if(bookings.IsElectricianRequired(dfSelectedEvent)):
                st.markdown("> You have booked equpiment that requires a qualified electrical technician to safely install and operate.")
                if(bookings.isBartenderBooked(dfSelectedEvent)):
                    st.markdown("> You **DO** have an electrician booked for this event and **DO NOT** need to book another.")
                else:
                    st.markdown('> ** YOU DO NOT HAVE AN ELECTRICIAN BOOKED FOR THIS EVENT AND MUST BOOK ONE BEFORE THE EVENT CAN BE APPROVED.')

            if bookings.isMandatoryStaffPersonPresent(dfSelectedEvent):
                st.markdown("> All events are required to book one mandatory staff person tasked with overseeing the event.  This is part of the terms of service for using this applicaiton.")

            st.markdown("##### In order for your event to be approved, it must pass these checks:")
            if(bookings.isMandatoryStaffPersonPresent(dfSelectedEvent)):
                st.write(bookings.isMandatoryStaffPersonPresent(dfSelectedEvent))
                st.markdown("You **DO** currently have the mandatory staff person employed for the event.")
            else:
                st.markdown("You **DO NOT** currently have the mandatory staff person employed to supervise your event.")
            if(bookings.isEvent_Over21(dfSelectedEvent)):
                if(bookings.isBartenderBooked(dfSelectedEvent)):
                    st.markdown("You **DO** currently have a bartender booked for this event.")
                else:
                    st.markdown("You **DO NOT** currently have a bartender booked for this event and require one.")
            if(bookings.isElectricianPresent(dfSelectedEvent) and bookings.qIsElectricianRequired(dfSelectedEvent)):
                st.markdown("You **DO** currently have an electrician booked for this event.")
            else:
                st.markdown("You **DO NOT** currently have a electrician booked for this event and require one.")

            st.markdown("> Please note that an electrician can simultaneously supervise and event.")

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
            dfQualifiedStaff['name'] = dfQualifiedStaff['first_name'] + dfQualifiedStaff['last_name']
            # Selection box for venues
            aAvailableID = dfQualifiedStaff['name'].tolist()
            aAvailableKey = dfQualifiedStaff['typeid'].tolist()
            dicAvailable = dict(zip(aAvailableKey, aAvailableID))
            selectedResource = st.selectbox('Select a new venue you would like to book:', aAvailableKey, format_func= lambda x: dicAvailable[x])
            
            # Get selected resource details in case of booking
            qSelectedResourceDetails = "SELECT * FROM resources_staff R WHERE R.typeid = " + str(selectedResource) + ";"
            dfSelectedResourceDetails = functions.query_db(qSelectedResourceDetails)

            st.write(dfSelectedResourceDetails)

            st.markdown("##### Would you like to book this resource?")
            if st.button('Reserve this Resource!'):
                bookings.makeBooking(dfSelectedEvent, dfSelectedResourceDetails, 1)
                st.markdown('Resource Booked!')
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
        dfEventsAll = functions.query_db_no_cache(qFetchEvents)

        if(dfEventsAll.empty):
            st.markdown("Hello, new user!  Select 'Make an Event' to create a new event!")

        # create a callable dictionary of name:id pairs for the select box
        dfEventSelect = dfEventsAll[['event_name', 'eventid']]
        aEventSelectName = dfEventSelect['event_name'].tolist()
        aEventSelectID = dfEventSelect['eventid'].tolist()
        dic = dict(zip(aEventSelectID, aEventSelectName))
        selectedEvent = st.selectbox('Select an event whose bookings you would like to edit:', aEventSelectID, format_func=lambda x: dic[x])

        # use the selected event to extract the event row for the selected event
        qSelectedDetails = "SELECT * FROM events E WHERE E.event_planner_email LIKE '" + user + \
                            "' AND eventid = " + str(selectedEvent) + " ORDER BY date, start_at;"
        dfSelectedEvent = functions.query_db_no_cache(qSelectedDetails)
        
        # Get the list of all resources already booked for this event
        qBookedResources = "SELECT B.description, B.resourcetype, B.typeid, B.cost, B.start_at, B.end_at FROM bookings B WHERE eventid = " + str(dfSelectedEvent['eventid'][0]) + ";"
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

        selectedResourceType = st.selectbox('Select the type of resource you would like to cancel:', dfBookableResources['enumlabel'])

         # Selection box for venues
        aAvailableID = dfBookedResources['description'].tolist()
        aAvailableKey = dfBookedResources['typeid'].tolist()
        dicAvailable = dict(zip(aAvailableKey, aAvailableID))
        selectedResource = st.selectbox('Select the resource you would like to cancel:', aAvailableKey, format_func= lambda x: dicAvailable[x])

        # Get selected resource details in case of booking
        qSelectedResourceDetails = "SELECT * FROM resources R WHERE R.resourcetype = '" + str(selectedResourceType) + "' AND R.typeid = " + str(selectedResource) + ";"
        dfSelectedResourceDetails = functions.query_db(qSelectedResourceDetails)

        st.write(dfSelectedResourceDetails)

        if (st.button('Cancel this Resource')):
            bookings.deleteBooking(dfSelectedEvent, dfSelectedResourceDetails)
            st.markdown('Resource Booking Cancelled.')


        
    elif(action == "Cancel an Event"):
        # fetch the list of all events
        qFetchEvents = "SELECT * FROM events E WHERE E.event_planner_email LIKE '" + user + \
            "' ORDER BY date, start_at;"
        dfEventsAll = functions.query_db_no_cache(qFetchEvents)

        if(dfEventsAll.empty):
            st.markdown("Hello, new user!  Select 'Make an Event' to create a new event!")

        # create a callable dictionary of name:id pairs for the select box
        dfEventSelect = dfEventsAll[['event_name', 'eventid']]
        aEventSelectName = dfEventSelect['event_name'].tolist()
        aEventSelectID = dfEventSelect['eventid'].tolist()
        dic = dict(zip(aEventSelectID, aEventSelectName))
        selectedEvent = st.selectbox('Select an event you would like to cancel:', aEventSelectID, format_func=lambda x: dic[x])

        try:
            # use the selected event to extract the event row for the selected event
            qSelectedDetails = "SELECT * FROM events E WHERE E.event_planner_email LIKE '" + user + \
                                "' AND eventid = " + str(selectedEvent) + " ORDER BY date, start_at;"
            dfSelectedEvent = functions.query_db_no_cache(qSelectedDetails)
            
            if (st.button('Cancel this Event')):
                bookings.deleteEvent(dfSelectedEvent)
                st.markdown('Your Event Has Been Cancelled.')
        except:
            st.markdown('It appears you have no events currently!')
    
