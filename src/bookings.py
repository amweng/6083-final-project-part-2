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
                     "WHERE B.resourcetype = '" + str(resourceType) + "' " + \
                     "AND B.typeid = " + str(resourceID) + ";"
    dfIsOverlapping = functions.query_db(qIsOverlapping)

    for idx in range(len(dfIsOverlapping['overlaps'])):
        if dfIsOverlapping['overlaps'][idx] == True:
            return False
    return True

def getAllAvailable(resourceType: str, timeWindow: pandas.DataFrame):
    
    if(resourceType == 'Caterer'):
        resourcesTable = 'resources_caterers'
    elif(resourceType == 'Entertainment'):
        resourcesTable = 'resources_entertainment'
    elif(resourceType == 'Equipment'):
        resourcesTable = 'resources_equipment'
    elif(resourceType == 'Staff'):
        resourcesTable = 'resources_staff'
    elif(resourceType == 'Venue'):
        resourcesTable = 'resources_venues'
    else:
        resourcesTable = "INVALID_TYPE"
    
    qAllAvailable = "SELECT * " + \
                   "FROM " + resourcesTable + \
                   " WHERE typeid NOT IN " + \
                   "(SELECT typeid FROM " + \
                   "(SELECT ('" + str(timeWindow['start_at'][0]) + "','" + str(timeWindow['end_at'][0]) +"')" + \
                   "OVERLAPS (B.start_at, B.end_at), B.typeid " + \
                   "FROM bookings B " + \
                   "WHERE B.resourcetype = '" + resourceType + "') B " + \
                   "WHERE B.overlaps = 'true');"
    
    return functions.query_db(qAllAvailable)

def getAllResourceRequirements():
    # Returns a recursively constructed 'bill of materials' over the resources_require table
    qResourcesRequire = "WITH RECURSIVE Requires(r1resourcetype, r1typeid, r2resourcetype, r2typeid) as ( \
	SELECT r1resourcetype, r1typeid, r2resourcetype, r2typeid FROM resources_require \
	UNION \
	SELECT 	R.r1resourcetype, R.r1typeid, Q.r2resourcetype, Q.r2typeid \
	FROM	Requires R, Resources_Require Q \
	WHERE	R.r2resourcetype = Q.r1resourcetype \
	AND	R.r2typeid = Q.r1typeid \
    ) \
    SELECT * FROM Requires ORDER BY r1resourcetype, r1typeid, r2resourcetype, r2typeid;"

    return functions.query_db_no_cache(qResourcesRequire)

def getRequiredResources(resourceType: str, resourceID: str):
    qResourceRequires = "WITH RECURSIVE Requires(r1resourcetype, r1typeid, r2resourcetype, r2typeid) as ( \
	SELECT r1resourcetype, r1typeid, r2resourcetype, r2typeid FROM resources_require \
	UNION \
	SELECT 	R.r1resourcetype, R.r1typeid, Q.r2resourcetype, Q.r2typeid \
	FROM	Requires R, Resources_Require Q \
	WHERE	R.r2resourcetype = Q.r1resourcetype \
	AND	R.r2typeid = Q.r1typeid \
    ) \
    SELECT * FROM Requires \
    WHERE r1resourcetype = " + str(resourceType) + " \
    AND r1typeid = " + str(resourceID) + \
    " ORDER BY r1resourcetype, r1typeid, r2resourcetype, r2typeid;"

    return functions.query_db_no_cache(qResourceRequires)

def isResourceQtyAvailable(resourceType: str, resourceID: int, timeWindow: pandas.DataFrame, qty: int):
    # Queries the resources table and bookings table to compute math over whether there exists a sufficient quantity for booking
    # Returns a boolean
    # Assumes timeWindow is a dataframe of the format (eventID, date, start_at, end_at) from events table
    return True

def isStaffAvailableQualified(qualificationType: str, timeWindow: pandas.DataFrame):
    if(qualificationType == 'None (ie, General Labourer)'):
        qQualifiedAvailableStaff = "SELECT * " + \
                                "FROM resources_staff S, qualifications_have Q " + \
                                "WHERE S.typeid NOT IN " + \
                                "(SELECT typeid FROM " + \
                                "(SELECT ('" + str(timeWindow['start_at'][0]) + "','" + str(timeWindow['end_at'][0]) +"')" + \
                                "OVERLAPS (B.start_at, B.end_at), B.typeid " + \
                                "FROM bookings B " + \
                                "WHERE B.resourcetype = 'Staff') B " + \
                                "WHERE B.overlaps = 'true') " + \
                                "AND S.email like Q.staff_email;"
    else:
        qQualifiedAvailableStaff = "SELECT * " + \
                                "FROM resources_staff S, qualifications_have Q " + \
                                "WHERE S.typeid NOT IN " + \
                                "(SELECT typeid FROM " + \
                                "(SELECT ('" + str(timeWindow['start_at'][0]) + "','" + str(timeWindow['end_at'][0]) +"')" + \
                                "OVERLAPS (B.start_at, B.end_at), B.typeid " + \
                                "FROM bookings B " + \
                                "WHERE B.resourcetype = 'Staff') B " + \
                                "WHERE B.overlaps = 'true') " + \
                                "AND S.email like Q.staff_email " + \
                                "AND Q.qualification = '" + qualificationType + "';"
    
    return functions.query_db(qQualifiedAvailableStaff)

def makeBooking(dfSelectedEvent: pandas.DataFrame, dfSelectedResource: pandas.DataFrame, qty: int):
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
        qVenueInsert = "INSERT INTO bookings VALUES (" + str(dfSelectedEvent['eventid'][0]) + ",'" + resourceType + "'," + str(typeID) + "," + \
                        str(dfSelectedEvent['start_at'][0]) + "," + str(dfSelectedEvent['end_at'][0]) + "," + str(dfSelectedResource['fee'][0]) + "," + \
                        "1, '" + str(dfSelectedResource['name'][0]) + "');"
        dfVoid = query_db(qVenueInsert)
        
    resourceType = str(dfSelectedResource['resourcetype'][0])
    resourceID = str(dfSelectedResource['typeid'][0])
    if(isResourceAvailable(resourceType, resourceID, dfSelectedEvent)):
        if(resourceType == 'Caterer'):
            bookCaterer()
        elif(resourceType == 'Entertainment'):
            bookEntertainment()
        elif(resourceType == 'Equipment'):
            if(isResourceQtyAvailable):
                bookEquipment()
            else:
                qResourceName = "SELECT specification FROM resources WHERE resourcetype = '" + resourceType + "' AND resource ID like " + str(resourceID) + ";"
                dfResourceName = functions.query_db(qResourceName)
                aResourceName = []
                st.markdown('The ' + dfResourceName['specification'][0] + ' that you requested is not available in sufficient quantity.')
        elif(resourceType == 'Staff'):
            bookStaff()
        elif(resourceType == 'Venue'):
            bookVenue()
        else:
            st.text('Please select a valid booking type.\n \
            Ensure your selection comes from the following, case-sensitive list: \n\
            Caterer, Entertainment, Equipment, Staff, Venue')
    else:
        st.markdown('The resource you requested is not available at that time.')