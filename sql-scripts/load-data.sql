BEGIN;

DELETE FROM resources;
DELETE FROM resources_entertainment;

CREATE TEMPORARY TABLE temp_resources_entertainment(
   	resourceType		resourceType NOT NULL,
	typeID			integer NOT NULL,
	fee			numeric(16,2) DEFAULT 0.00 NOT NULL,
	specification		varchar(256),
	name			varchar(128) UNIQUE NOT NULL,
	genre			varchar(64) NOT NULL,
	contentRating		contentRating NOT NULL,
	spaceRequired		integer,
	PRIMARY KEY (resourceType, typeID)
);


COPY temp_resources_entertainment(resourceType, typeID, fee, specification, name, genre, contentRating, spaceRequired)
FROM '/Users/andrewweng/Developer/databases/6083-final-project-part-2/data/resources_entertainment.csv'
DELIMITER ',' CSV;

INSERT INTO resources_entertainment
SELECT resourceType, typeID, fee, specification, name, genre, contentRating, spaceRequired
FROM temp_resources_entertainment;

SELECT setval('resources_entertainment_typeid_seq', (SELECT MAX(typeID) from resources_entertainment), true);

DROP TABLE temp_resources_entertainment;

COMMIT;	
