BEGIN;


DELETE FROM resources_require;
DELETE FROM menus_accommodate;
DELETE FROM menus_offered;
DELETE FROM dietary_restrictions_have;
DELETE FROM guests_attend;
DELETE FROM events;
DELETE FROM event_planners;
DELETE FROM resources CASCADE;
DELETE FROM bookings;

----------------------------------------------------------------------

CREATE TEMPORARY TABLE temp_resources_entertainment(
	resourceType		resourceType NOT NULL,
	typeID			integer NOT NULL,
	fee			numeric(16,2) DEFAULT 0.00 NOT NULL,
	specification		varchar(128),
	name			varchar(128) UNIQUE NOT NULL,
	genre			varchar(64) NOT NULL,
	contentRating		contentRating NOT NULL,
	spaceRequired		integer,
	PRIMARY KEY (typeID)
) ON COMMIT DROP;

\copy temp_resources_entertainment FROM '~/6083-final-project-part-2/data/resources_entertainment.csv' WITH CSV;

INSERT INTO resources
SELECT resourceType, typeID, specification
FROM temp_resources_entertainment;

INSERT INTO resources_entertainment
SELECT resourceType, typeID, name, fee, genre, contentRating, spaceRequired
FROM temp_resources_entertainment;

----------------------------------------------------------------------

CREATE TEMPORARY TABLE temp_resources_equipment(
	resourceType		resourceType NOT NULL,
	typeID			integer NOT NULL,
	fee			numeric(16,2) DEFAULT 0.00 NOT NULL,
	specification		varchar(128),
	name			varchar(128) UNIQUE NOT NULL,
	equipmentType		varchar(128) NOT NULL,
	quantity		integer NOT NULL,
	vendor			varchar(128),
	PRIMARY KEY (typeID)
) ON COMMIT DROP;

\copy temp_resources_equipment FROM '~/6083-final-project-part-2/data/resources_equipment.csv' WITH CSV;

INSERT INTO resources
SELECT resourceType, typeID, specification
FROM temp_resources_equipment;

INSERT INTO resources_equipment
SELECT resourceType, typeID, name, fee, equipmentType, quantity, vendor
FROM temp_resources_equipment;


----------------------------------------------------------------------

CREATE TEMPORARY TABLE temp_resources_venues(
	resourceType		resourceType NOT NULL,
	typeID			integer NOT NULL,
	fee			numeric(16,2) DEFAULT 0.00 NOT NULL,
	specification		varchar(128),
	name			varchar(128) UNIQUE NOT NULL,
	address			varchar(128) NOT NULL,
	roomNum			varchar(32),
	capacity		integer DEFAULT 0 NOT NULL,
	stageArea		integer,
	liquorLicense		boolean DEFAULT false,
	PRIMARY KEY (typeID)
) ON COMMIT DROP;

\copy temp_resources_venues FROM '~/6083-final-project-part-2/data/resources_venues.csv' WITH CSV;

INSERT INTO resources
SELECT resourceType, typeID, specification
FROM temp_resources_venues;

INSERT INTO resources_venues
SELECT resourceType, typeID, name, fee, address, roomNum, capacity, stageArea, liquorLicense
FROM temp_resources_venues;

----------------------------------------------------------------------

CREATE TEMPORARY TABLE temp_resources_staff(
	resourceType		resourceType NOT NULL,
	typeID			integer NOT NULL,
	fee			numeric(16,2) DEFAULT 0.00 NOT NULL,
	specification		varchar(128),
	pronoun			varchar(64) NOT NULL,
	first_name		varchar(128) NOT NULL,
	last_name		varchar(128) NOT NULL,
	email			varchar(128) UNIQUE NOT NULL,
	PRIMARY KEY (typeID)
) ON COMMIT DROP;

\copy temp_resources_staff FROM '~/6083-final-project-part-2/data/resources_staff.csv' WITH CSV;

INSERT INTO resources
SELECT resourceType, typeID, specification
FROM temp_resources_staff;

INSERT INTO resources_staff
SELECT resourceType, typeID, fee, pronoun, first_name, last_name, email
FROM temp_resources_staff;


----------------------------------------------------------------------

CREATE TEMPORARY TABLE temp_resources_caterers(
	resourceType		resourceType NOT NULL,
	typeID			integer NOT NULL,
	fee			numeric(16,2) DEFAULT 0.00 NOT NULL,
	specification		varchar(128),
	name			varchar(128) UNIQUE NOT NULL,
	PRIMARY KEY (typeID)
) ON COMMIT DROP;

\copy temp_resources_caterers FROM '~/6083-final-project-part-2/data/resources_caterers.csv' WITH CSV;

INSERT INTO resources
SELECT resourceType, typeID, specification
FROM temp_resources_caterers;

INSERT INTO resources_caterers
SELECT resourceType, typeID, name, fee
FROM temp_resources_caterers;

\copy event_planners FROM '~/6083-final-project-part-2/data/event_planners.csv' WITH CSV;
\copy events FROM '~/6083-final-project-part-2/data/events.csv' WITH CSV;
\copy guests_attend FROM '~/6083-final-project-part-2/data/guests_attend.csv' WITH CSV;
\copy dietary_restrictions_have FROM '~/6083-final-project-part-2/data/dietary_restrictions_have.csv' WITH CSV;
\copy menus_offered FROM '~/6083-final-project-part-2/data/menus_offered.csv' WITH CSV;
\copy menus_accommodate FROM '~/6083-final-project-part-2/data/menus_accommodate.csv' WITH CSV;
\copy resources_require FROM '~/6083-final-project-part-2/data/resources_require.csv' WITH CSV;
\copy qualifications_have FROM '~/6083-final-project-part-2/data/qualifications_have.csv' WITH CSV;
\copy bookings FROM '~/6083-final-project-part-2/data/bookings.csv' WITH CSV;

-- LEGACY

--\copy resources_equipment FROM '~/6083-final-project-part-2/data/resources_equipment.csv' WITH CSV;
--SELECT setval('resources_equipment_typeid_seq', (SELECT MAX(typeID) from resources_equipment), true);

--\copy resources_venues FROM '~/6083-final-project-part-2/data/resources_venues.csv' WITH CSV;
--SELECT setval('resources_venues_typeid_seq', (SELECT MAX(typeID) from resources_venues), true);

--\copy resources_staff FROM '~/6083-final-project-part-2/data/resources_staff.csv' WITH CSV;
--SELECT setval('resources_staff_typeid_seq', (SELECT MAX(typeID) from resources_staff), true);

--\copy resources_caterers FROM '~/6083-final-project-part-2/data/resources_caterers.csv' WITH CSV;
--SELECT setval('resources_caterers_typeid_seq', (SELECT MAX(typeID) from resources_caterers), true);

COMMIT;	
