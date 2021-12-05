import functions
import datetime as dt
import pytz
import pandas

def isResourceAvailable(resourceType: str, resourceID: int, timeWindow: pandas.DataFrame):
    # Queries the bookings database for whether a resource has been booked for that time window
    # Returns a boolean
    # Assumes timeWindow comes from a dataframe with the columsn (eventID, date, start_at, end_at) from events table
    qIsOverlapping = "SELECT ('" + str(timeWindow['start_at'][0]) + "','" + str(timeWindow['end_at'][0]) + "') " + \
                     "OVERLAPS (B.start_at, B.end_at) FROM bookings B " + \
                     "WHERE B.eventid = " + str(timeWindow['eventid'][0]) + " " + \
                     "AND B.resourcetype = '" + str(resourceType) + "' " + \
                     "AND B.typeid <> " + str(resourceID) + ";"
    dfIsOverlapping = functions.query_db(qIsOverlapping)

    for idx in range(len(dfIsOverlapping['overlaps'])):
        if dfIsOverlapping['overlaps'][idx] == True:
            return (False, dfIsOverlapping)
    return (True, dfIsOverlapping)

def isResourceQtyAvailable(resourceType: str, resourceID: int, timeWindow: pandas.DataFrame, qty: int):
    # Queries the resources table and bookings table to compute math over whether there exists a sufficient quantity for booking
    # Returns a boolean
    # Assumes timeWindow is a dataframe of the format (eventID, date, start_at, end_at) from events table
    return True

def makeBooking(eventID: int, resourceType: str, typeID: int, qty: int):
    qEventEntry = "SELECT E.eventid, E.date, E.start_at, E.end_at FROM events E WHERE E.eventid = " + eventID + ";"
    dfEventEntry = query_db(qEventEntry)

    def bookCaterer(dfEventEntry: pandas.DataFrame, resourceType: str, resourceID: int, qty: int):
        qCatererDetails = "" #DO WE BOOK THE CATERER OR THE MENU (AND THE CATERER JUST COMES ALONG?)
        pass

    def bookEntertainment():
        qEntertainerDetails = "SELECT R.name, R.fee FROM resources_entertainment R WHERE typeid = " + resourceID + ";"
        dfEntertainerDetails = functions.query_db(qEntertainerDetails)
        aEventID = dfEventEntry['eventid'][0]
        aEntertainerFee = dfEntertainerDetails['fee'][0]
        aEntertainerName = dfEntertainerDetails['name'][0]

        qEntertainerInsert = "INSERT INTO bookings(eventid, resourcetype, typeid, start_at, end_at, cost, num, description) VALUES(" + \
                            dfEventEntry['eventid'][0] + ',' + \
                            '\'' + resourceType +'\',' + \
                            typeID + ',' + \
                            dfEventEntry['start_at'][0] + ',' + \
                            dfEventEntry['end_at'][0] + ',' + \
                            aEntertainerFee + ',' + \
                            '1,\'' + aEntertainerName + \
                            "\');"
        dfVoid = query_db(qEntertainerInsert)
        pass

    def bookEquipment():
        pass

    def bookStaff():
        pass

    def bookVenue():
        pass

    if(isResourceAvailable(resourceType, resourceID, dfEventEntry)):
        if(resourceType == 'Caterer'):
            bookCaterer()
            pass
        elif(resourceType == 'Entertainment'):
            bookEntertainment()
            pass
        elif(resourceType == 'Equipment'):
            if(isResourceQtyAvailable):
                bookEquipment()
            else:
                qResourceName = "SELECT specification FROM resources WHERE resourcetype = '" + resourceType + "' AND resource ID like " + str(resourceID) + ";"
                dfResourceName = functions.query_db(qResourceName)
                aResourceName = []
                st.markdown('The ' + dfResourceName['specification'][0] + ' that you requested is not available in sufficient quantity.')
            pass
        elif(resourceType == 'Staff'):
            bookStaff()
            pass
        elif(resourceType == 'Venue'):
            bookVenue()
            pass
        else:
            st.text('Please select a valid booking type.\n \
            Ensure your selection comes from the following, case-sensitive list: \n\
            Caterer, Entertainment, Equipment, Staff, Venue')
    else:
        st.markdown('The resource you requested is not available at that time.')