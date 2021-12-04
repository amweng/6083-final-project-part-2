BEGIN;

DELETE FROM resources_entertainment;
DELETE FROM resources_equipment;
DELETE FROM resources_venues;
DELETE FROM resources_staff;
DELETE FROM menus_accommodate;
DELETE FROM menus_offered;
DELETE FROM resources_caterers;
DELETE FROM dietary_restrictions_have;
DELETE FROM guests_attend;
DELETE FROM events;
DELETE FROM event_planners;

\copy resources_entertainment FROM '~/6083-final-project-part-2/data/resources_entertainment.csv' WITH CSV;
SELECT setval('resources_entertainment_typeid_seq', (SELECT MAX(typeID) from resources_entertainment), true);

\copy resources_equipment FROM '~/6083-final-project-part-2/data/resources_equipment.csv' WITH CSV;
SELECT setval('resources_equipment_typeid_seq', (SELECT MAX(typeID) from resources_equipment), true);

\copy resources_venues FROM '~/6083-final-project-part-2/data/resources_venues.csv' WITH CSV;
SELECT setval('resources_venues_typeid_seq', (SELECT MAX(typeID) from resources_venues), true);

\copy resources_staff FROM '~/6083-final-project-part-2/data/resources_staff.csv' WITH CSV;
SELECT setval('resources_staff_typeid_seq', (SELECT MAX(typeID) from resources_staff), true);

\copy resources_caterers FROM '~/6083-final-project-part-2/data/resources_caterers.csv' WITH CSV;
SELECT setval('resources_caterers_typeid_seq', (SELECT MAX(typeID) from resources_caterers), true);

\copy event_planners FROM '~/6083-final-project-part-2/data/event_planners.csv' WITH CSV;
\copy events FROM '~/6083-final-project-part-2/data/events.csv' WITH CSV;
\copy guests_attend FROM '~/6083-final-project-part-2/data/guests_attend.csv' WITH CSV;
\copy dietary_restrictions_have FROM '~/6083-final-project-part-2/data/dietary_restrictions_have.csv' WITH CSV;
\copy menus_offered FROM '~/6083-final-project-part-2/data/menus_offered.csv' WITH CSV;
\copy menus_accommodate FROM '~/6083-final-project-part-2/data/menus_accommodate.csv' WITH CSV;


COMMIT;	
