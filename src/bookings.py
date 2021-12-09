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
    SELECT Q.r1resourcetype, Q.r1typeid, E1.name as item, Q.r2resourcetype, Q.r2typeid, E2.name as requires, E2.fee \
    FROM resources_equipment E1, resources_equipment E2, Requires Q \
    WHERE Q.r1resourcetype = '" + str(resourceType) + "' " + \
    "AND Q.r1typeid = " + str(resourceID) + \
    " AND E1.typeid = Q.r1typeid AND E2.typeid = Q.r2typeid"
    " ORDER BY r1resourcetype, r1typeid, r2resourcetype, r2typeid;"

    return functions.query_db_no_cache(qResourceRequires)

# my implmentation of this function differs slightly in that: If two resources require the same piece
# of equipment but in differing quantities, we select the line-item requirement that requires a higher
# quantity and we list that as the reason.
#
# Ex: If lighting-set requires 2 power supply and fog machine requires 1, then we list the req. for 2
# power machines and the specification that lighting-set requires 2 power supply.
def getVendorEquipmentReq(resourceType: str, typeID: int):
    q_get_vendor_equipment_req = "WITH RECURSIVE Dependencies(r1resourceType, r1typeID, r2resourceType, r2typeID, numRequired, specification)" \
                                    " AS (SELECT r1resourceType, r1typeID, r2resourceType, r2typeID, numRequired, specification" \
                                    " FROM resources_require WHERE (r1resourceType, r1typeID) != (r2resourceType, r2typeID)" \
                                    " UNION" \
                                    " SELECT D.r1resourceType, D.r1typeID, RR.r2resourceType, RR.r2typeID, RR.numRequired, RR.specification" \
                                    " FROM   Dependencies D, resources_require RR" \
                                    " WHERE  (D.r2resourceType, D.r2typeID) = (RR.r1resourceType, RR.r1typeID)" \
                                    " AND (D.r1resourceType, D.r1typeID) != (D.r2resourceType, D.r2typeID))" \
                                " SELECT * FROM (SELECT RE.resourceType, RE.name, RE.fee, D.numRequired, D.specification" \
                                    " FROM Dependencies D, resources_equipment RE" \
                                    " WHERE (D.r2resourcetype, D.r2typeID) = (RE.resourceType, RE.typeID)" \
                                    " AND D.r1resourceType = '" + resourceType + "'" \
                                    " AND D.r1typeID = "+ str(typeID) + " ) AS VD" \
                                    " WHERE (name, numRequired) IN (" \
                                        " SELECT vd.name, MAX(vd.numRequired)" \
                                            " FROM (SELECT RE.name, D.numRequired" \
                                            " FROM Dependencies D, resources_equipment RE" \
                                            " WHERE (D.r2resourcetype, D.r2typeID) = (RE.resourceType, RE.typeID)" \
                                            " AND D.r1resourceType = '" + resourceType + "'" \
                                            " AND D.r1typeID = "+ str(typeID) + " ) AS VD" \
                                " GROUP BY vd.name);"

    return functions.query_db(q_get_vendor_equipment_req)

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

def isMandatoryStaffPersonPresent(timeWindow: pandas.DataFrame):
    qIsStaffPersonPresent = "SELECT CASE WHEN EXISTS ( \
                                SELECT * \
                                FROM bookings B \
                                WHERE resourcetype = 'Staff' \
                                AND typeid IS NOT NULL \
                                AND ('" + str(timeWindow['start_at'][0]) + "','" + str(timeWindow['end_at'][0]) + "') \
                                    OVERLAPS (start_at, end_at)) \
                            THEN CAST(1 AS BIT) \
                            ELSE CAST(0 AS BIT) \
                            END;"
    return (functions.query_db_no_cache(qIsStaffPersonPresent)['case'][0] == 1)

def isElectricianPresent(timeWindow: pandas.DataFrame):
    qIsElectricianPresent = "SELECT CASE WHEN EXISTS (\
                                SELECT * \
                                FROM bookings B, resources_staff R, qualifications_have Q \
                                WHERE 	B.resourcetype = 'Staff' \
                                AND	B.typeid IS NOT NULL \
                                AND ('" + str(timeWindow['start_at'][0]) + "','" + str(timeWindow['end_at'][0]) + "') \
                                    OVERLAPS (B.start_at, B.end_at) \
                                AND	B.typeid = R.typeid \
                                AND	R.email = Q.staff_email \
                                AND	Q.qualification = 'Electrical') \
                            THEN CAST (1 AS BIT) \
                            ELSE CAST (0 AS BIT) \
                            END;"
    return (functions.query_db_no_cache(qIsElectricianPresent)['case'][0] == 1)

def getAllDietaryRestrictions(dfEvent: pandas.DataFrame):
    qAllDietaryRestrictions = "SELECT 	GA.eventid, GA.email, DR.restriction, DR.severity \
                            FROM	guests_attend GA, dietary_restrictions_have DR \
                            WHERE	GA.eventid = '" + str(dfEvent['eventid'][0]) + "' \
                            AND	GA.email = DR.email \
                            ORDER BY restriction, severity, email;"
    return functions.query_db(qAllDietaryRestrictions)

def getAllAccomodatingMenus(dfEvent: pandas.DataFrame):
    qAllAccomodatingMenus = "SELECT  MO.menuid, MO.name, MO.caterer_name, count(MA.accommodation) as accommodation_rank \
                            FROM	menus_offered MO, menus_accommodate MA \
                            WHERE	MO.menuid = MA.menuid \
                            AND	MA.accommodation IN ( SELECT 	DR.restriction \
                                FROM	guests_attend GA, dietary_restrictions_have DR \
                                WHERE	GA.eventid = '" + str(dfEvent['eventid'][0]) + "' \
                                AND	GA.email = DR.email) \
                            AND MO.caterer_name IN ( \
                                SELECT name FROM resources_caterers \
                                EXCEPT \
                                SELECT description as name \
                                FROM bookings \
                                WHERE resourcetype = 'Caterer' \
                                AND ('" + str(dfEvent['start_at'][0]) + "','" + str(dfEvent['end_at'][0]) + "') \
                                    OVERLAPS (bookings.start_at, bookings.end_at)) \
                            GROUP BY MO.menuid, MO.name, MO.caterer_name \
                            ORDER BY accommodation_rank DESC, menuid, name;"
    return functions.query_db(qAllAccomodatingMenus)

def getCaterersAccomodatingMenus(dfEvent: pandas.DataFrame, dfResource: pandas.DataFrame):
    qCaterersAccomodatingMenus = "SELECT distinct name as menu_name, accommodation\
                                FROM (	SELECT 	MO.menuid, MO.caterer_name, MO.name, MA.accommodation \
                                    FROM	menus_offered MO full join menus_accommodate MA \
                                    ON	MO.menuid = MA.menuid \
                                    ORDER BY MO.caterer_name, MO.name, MA.accommodation ) A \
                                WHERE accommodation IN (  \
                                    SELECT 	DR.restriction \
                                    FROM	guests_attend GA, dietary_restrictions_have DR \
                                    WHERE	GA.eventid = " + str(dfEvent['eventid'][0]) + " \
                                    AND	GA.email = DR.email) \
                                AND	caterer_name = '" + str(dfResource['name'][0]) + "';"
    return functions.query_db(qCaterersAccomodatingMenus)

def getAllCatererMenusPlusAccomodations(dfEvent: pandas.DataFrame, dfResource: pandas.DataFrame):
    qAllCatererMenusPlusAccomodations = "SELECT menuid, name, accommodation FROM ( \
                                            SELECT 	MO.menuid, MO.name, MO.caterer_name, MA.accommodation \
                                            FROM	menus_offered MO full join menus_accommodate MA \
                                            ON	MO.menuid = MA.menuid) A \
                                        WHERE caterer_name = '" + str(dfResource['name'][0]) + "' \
                                        ORDER BY name;"
    return functions.query_db(qAllCatererMenusPlusAccomodations)

def isEvent_Over21(dfEvent: pandas.DataFrame):
    qIsEventOver21 = "SELECT over_21 FROM events WHERE eventid = " + str(dfEvent['eventid'][0]) + ";"
    return functions.query_db(qIsEventOver21)['over_21'][0]

def isBartenderBooked(dfEvent: pandas.DataFrame):
    qIsBartenderBooked = "SELECT CASE WHEN EXISTS (SELECT * \
                            FROM 	bookings B, resources_staff R, qualifications_have Q \
                            WHERE 	B.resourcetype = 'Staff' \
                            AND	B.typeid IS NOT NULL \
                            AND 	('" + str(dfEvent['start_at'][0]) + "','" + str(dfEvent['end_at'][0]) + "') OVERLAPS (B.start_at, B.end_at) \
                            AND	B.typeid = R.typeid \
                            AND	R.email = Q.staff_email \
                            AND	Q.qualification = 'Bartending') \
                        THEN CAST (1 AS BIT) \
                        ELSE CAST (0 AS BIT) \
                        END;"
    return (functions.query_db_no_cache(qIsBartenderBooked)['case'][0] == 1)

def bookRequiredResources(dfEvent: pandas.DataFrame, dfResource: pandas.DataFrame):
    # This code adapts Andrew's brilliant getVendorEquipmentReq() code into an iterative query for batch insertion
    # For the attentive reader interested in some specifics, note that the syntax is, broadly, 'INSERT INTO bookings () on conflict do nothing;'
    # This is because, we adopted the convention that if you already have a resource booked of a needed type, we claim that the
    # requirement is already satisfied.  Is this true to the real world?  No, but the point we sought to make was that it is
    # possible to programatically insert data using a recursive bill of materials, and this was accomplished.

    qReqResources2Book = "WITH RECURSIVE Dependencies(r1resourceType, r1typeID, r2resourceType, r2typeID, numRequired, specification) AS (\
                            SELECT	r1resourceType, r1typeID, r2resourceType, r2typeID, numRequired, specification \
                            FROM resources_require \
                            WHERE (r1resourceType, r1typeID) != (r2resourceType, r2typeID) \
                            UNION \
                            SELECT D.r1resourceType, D.r1typeID, RR.r2resourceType, RR.r2typeID, RR.numRequired, RR.specification \
                            FROM Dependencies D, resources_require RR \
                            WHERE (D.r2resourceType, D.r2typeID) = (RR.r1resourceType, RR.r1typeID) \
                            AND (D.r1resourceType, D.r1typeID) != (D.r2resourceType, D.r2typeID))    \
                        INSERT INTO bookings \
                        SELECT * FROM ( \
                            SELECT E.eventid, D.r2resourcetype, D.r2typeid, E.start_at, E.end_at, RE.fee as cost, D.numRequired as num, 	RE.name as description \
                            FROM	events E, dependencies D, resources_equipment RE \
                            WHERE	E.eventid = 1 \
                            AND	D.r1resourcetype = 'Equipment' \
                            AND	D.r1typeid = 29 \
                            AND	D.r2resourcetype = RE.resourcetype \
                            AND	RE.typeid = D.r2typeid) AS VD \
                        WHERE (description, num) IN ( \
                            SELECT vd.name, MAX(vd.numRequired) \
                            FROM (SELECT RE.name, D.numRequired \
                                FROM Dependencies D, resources_equipment RE \
                                WHERE (D.r2resourcetype, D.r2typeID) = (RE.resourceType, RE.typeID) \
                                AND D.r1resourceType = RE.resourceType \
                                AND D.r1typeID = 29) AS VD \
                            GROUP BY vd.name) ON CONFLICT (eventid, resourcetype, typeid) DO NOTHING;"
    functions.execute_db(qReqResources2Book)

def makeBooking(dfEvent: pandas.DataFrame, dfResource: pandas.DataFrame, qty: int=1):
    # This booking function expects that the resource has previously passed all checks for availabilty.
    # If a redundant booking occurs, please contact the service deparment immediately.

    if(dfResource['resourcetype'][0] == 'Venue'):
        qDropVenue = "DELETE FROM bookings WHERE eventid = " + str(dfEvent['eventid'][0]) + ";"
        functions.execute_db(qDropVenue)

        qInsertBooking =   "INSERT INTO bookings VALUES (" + str(dfEvent['eventid'][0]) + ",'" + str(dfResource['resourcetype'][0]) + \
                    "'," + str(dfResource['typeid'][0]) + ",'" + str(dfEvent['start_at'][0]) + "','" + str(dfEvent['end_at'][0]) + \
                    "'," + str(dfResource['fee'][0]) + "," + str(qty) + ",'" + str(dfResource['name'][0]) + "')  ON CONFLICT (eventid, resourcetype, typeid) DO NOTHING;"
        functions.execute_db(qInsertBooking)

        qModifyEventListing = "UPDATE events SET location = '" + str(dfResource['address'][0]) + "' WHERE eventid = " + str(dfEvent['eventid'][0]) + ";"
        functions.execute_db(qModifyEventListing)
    else:
        qInsertBooking =   "INSERT INTO bookings VALUES (" + str(dfEvent['eventid'][0]) + ",'" + str(dfResource['resourcetype'][0]) + \
                    "'," + str(dfResource['typeid'][0]) + ",'" + str(dfEvent['start_at'][0]) + "','" + str(dfEvent['end_at'][0]) + \
                    "'," + str(dfResource['fee'][0]) + "," + str(qty) + ",'" + str(dfResource['name'][0]) + "')  ON CONFLICT (eventid, resourcetype, typeid) DO NOTHING;"
        functions.execute_db(qInsertBooking)
        bookRequiredResources(dfEvent, dfResource)

