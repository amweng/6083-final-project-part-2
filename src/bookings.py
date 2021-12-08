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

def getAllAvailableEntertainers(eventID: int, resourceType: str, timeWindow: pandas.DataFrame):
    qAllAvailableEntertainers = "SELECT A.* " + \
                                "FROM (" + \
                                "SELECT E.* " + \
                                "FROM resources_entertainment E " + \
                                "WHERE E.spacerequired is null " + \
                                "UNION " + \
                                "SELECT E.* " + \
                                "FROM resources_entertainment E, (" + \
                                "SELECT V.address, V.stagearea " + \
                                "FROM events E, resources_venues V " + \
                                "WHERE E.eventid = " + str(eventID) + " " + \
                                "AND E.location = V.address) V " + \
                                "WHERE E.spacerequired is not null " + \
                                "AND E.spacerequired < V.stagearea) A " + \
                                "WHERE typeid NOT IN (" + \
                                "SELECT typeid " + \
                                "FROM (" + \
                                "SELECT ('" + str(timeWindow['start_at'][0]) + "','" + str(timeWindow['end_at'][0]) + "') " + \
                                "OVERLAPS (B.start_at, B.end_at), B.typeid " + \
                                "FROM bookings B " + \
                                "WHERE B.resourcetype = 'Entertainment') B " + \
                                "WHERE B.overlaps = 'true') " + \
                                "ORDER BY A.contentrating, A.fee, A.genre;"
    return functions.query_db_no_cache(qAllAvailableEntertainers)

def getAllAvailableVenues(eventID: int, resourceType: str, timeWindow: pandas.DataFrame):
    qAllAvailableVenues = "SELECT V.* " + \
                        "FROM resources_venues V " + \
                        "WHERE V.capacity > (" + \
                            "SELECT count(*) " + \
                            "FROM guests_attend G " + \
                            "WHERE G.eventid = 7) " + \
                        "AND V.stagearea > (" + \
                            "SELECT COALESCE(MAX(E.spacerequired),0) " + \
                            "FROM bookings B, resources_entertainment E " + \
                            "WHERE B.resourcetype = 'Entertainment' " + \
                            "AND B.eventid = " + str(eventID) + ") " + \
                        "AND typeid NOT IN (" + \
                                "SELECT typeid " + \
                                "FROM (" + \
                                "SELECT ('" + str(timeWindow['start_at'][0]) + "','" + str(timeWindow['end_at'][0]) + "') " + \
                                "OVERLAPS (B.start_at, B.end_at), B.typeid " + \
                                "FROM bookings B " + \
                                "WHERE B.resourcetype = 'Venue') B " + \
                                "WHERE B.overlaps = 'true') " + \
                        "ORDER BY V.capacity, V.address, V.roomnum;"
    return functions.query_db_no_cache(qAllAvailableVenues)

def getAllAvailable(eventid: int, resourceType: str, timeWindow: pandas.DataFrame):
    
    if(resourceType == 'Caterer'):
        resourcesTable = 'resources_caterers'
    elif(resourceType == 'Entertainment'):
        return getAllAvailableEntertainers(eventid, resourceType, timeWindow)
    elif(resourceType == 'Equipment'):
        resourcesTable = 'resources_equipment'
    elif(resourceType == 'Staff'):
        resourcesTable = 'resources_staff'
    elif(resourceType == 'Venue'):
        return getAllAvailableVenues(eventid, resourceType, timeWindow)
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

def isResourceQtyAvailable(resourceType: str, resourceID: int, timeWindow: pandas.DataFrame, qtyRequested: int):
    # Queries the resources table and bookings table to compute math over whether there exists a sufficient quantity for booking
    # Returns a boolean
    # Assumes timeWindow is a dataframe of the format (eventID, date, start_at, end_at) from events table

    # Implementation note: if a table is empty, SUM() returns a null value.  COALESCE(x,y) returns the first non-null value of (x,y)
    # So, COALECE(SUM(arg),0)) will pass 'arg' if not null and 0 if arg is null.
    qSufficientQty = "SELECT CASE WHEN " + str(qtyRequested) + " <= (" + \
                        "SELECT A.in_system - B.booked AS units_avail " + \
                        "FROM (SELECT quantity as in_system " + \
                            "FROM resources_equipment " + \
                            "WHERE typeid = " + str(resourceID) + ") A, " + \
                            "(SELECT COALESCE(sum(num),0) AS booked " + \
                            "WHERE resourcetype = '" + resourceType + "' " + \
                            "AND typeid = " + str(resourceID) + " " + \
                            "AND ('" + str(timeWindow['start_at'][0]) + "','" + str(timeWindow['end_at'][0]) + "') " + \
                    "OVERLAPS (start_at, end_at)) B) " + \
                    "THEN CAST (1 AS BIT) ELSE CAST (0 AS BIT) END;"
    
    return functions.query_db_no_cache(qSufficientQty)

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

def makeBooking(dfEvent: pandas.DataFrame, dfResource: pandas.DataFrame, qty: int=1):
    # This booking function expects that the resource has previously passed all checks for availabilty.
    # If a redundant booking occurs, please contact the service deparment immediately.

    if(dfResource['resourcetype'][0] == 'Venue'):
        qDropVenue = "DELETE FROM bookings WHERE eventid = " + str(dfEvent['eventid'][0]) + ";"
        functions.execute_db(qDropVenue)

        qInsertBooking =   "INSERT INTO bookings VALUES (" + str(dfEvent['eventid'][0]) + ",'" + str(dfResource['resourcetype'][0]) + \
                    "'," + str(dfResource['typeid'][0]) + ",'" + str(dfEvent['start_at'][0]) + "','" + str(dfEvent['end_at'][0]) + \
                    "'," + str(dfResource['fee'][0]) + "," + str(qty) + ",'" + str(dfResource['name'][0]) + "');"
        functions.execute_db(qInsertBooking)

        qModifyEventListing = "UPDATE events SET location = '" + str(dfResource['address'][0]) + "' WHERE eventid = " + str(dfEvent['eventid'][0]) + ";"
        functions.execute_db(qModifyEventListing)
    else:
        qInsertBooking =   "INSERT INTO bookings VALUES (" + str(dfEvent['eventid'][0]) + ",'" + str(dfResource['resourcetype'][0]) + \
                    "'," + str(dfResource['typeid'][0]) + ",'" + str(dfEvent['start_at'][0]) + "','" + str(dfEvent['end_at'][0]) + \
                    "'," + str(dfResource['fee'][0]) + "," + str(qty) + ",'" + str(dfResource['name'][0]) + "');"
        functions.execute_db(qInsertBooking)
    