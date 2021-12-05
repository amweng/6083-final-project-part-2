DROP TABLE events CASCADE;
DROP TABLE event_planners;
DROP TABLE Bookings CASCADE;
DROP TABLE guests_attend CASCADE;
DROP TABLE dietary_restrictions_have CASCADE;
DROP TABLE menus_offered CASCADE;
DROP TABLE menus_accommodate CASCADE;
DROP TABLE resources_require;
DROP TABLE resources_entertainment;
DROP TABLE resources_equipment;
DROP TABLE resources_venues;
DROP TABLE resources_staff CASCADE;
DROP TABLE resources_caterers;
DROP TABLE resources;
DROP TABLE qualifications_have;
DROP TYPE qualification;
DROP TYPE contentRating;
DROP TYPE resourceType;


CREATE TABLE Event_Planners (
	first_name		varchar(128) NOT NULL,
	last_name		varchar(128) NOT NULL,
	email			varchar(128) PRIMARY KEY,
	phone			varchar(128) NOT NULL,
	pronoun			varchar(16) NOT NULL
);

CREATE TABLE Events (
	eventID			integer PRIMARY KEY,
	date			date NOT NULL,
	start_at		time with time zone NOT NULL,
	end_at			time with time zone NOT NULL,
	location		varchar(128) NOT NULL,
	budget			numeric(16,2) DEFAULT 0.00,
	event_planner_email	varchar(128) NOT NULL,
	event_name		varchar(128) NOT NULL,
	over_21			boolean DEFAULT false,
	FOREIGN KEY (event_planner_email) REFERENCES Event_Planners (email)
);

CREATE TABLE Guests_Attend (
	eventID			integer,
	email			varchar(128),
	title			varchar(128),
	first_name		varchar(128) NOT NULL,
	last_name		varchar(128) NOT NULL,
	suffix			varchar(64),
	phone			varchar(32) NOT NULL,
	pronoun			varchar(16) NOT NULL,
	under_21		boolean DEFAULT false,
	UNIQUE(eventID,email),
	PRIMARY KEY (eventID,email),
	FOREIGN KEY (eventID) REFERENCES Events(eventID)
);

CREATE TABLE Dietary_Restrictions_Have (
	eventID		integer,
	email		varchar(128),
	restriction	varchar(128),
	severity	varchar(128),
	PRIMARY KEY (eventID, email, restriction),
	FOREIGN KEY (eventID, email) REFERENCES Guests_Attend(eventID, email) ON DELETE CASCADE
);


CREATE TYPE resourceType AS ENUM ('Entertainment', 'Equipment', 'Venue','Staff','Caterer');

CREATE TABLE Resources (
	resourceType		resourceType NOT NULL,
	typeID			integer NOT NULL,
	specification		varchar(256),
	PRIMARY KEY (resourceType, typeID)
);

CREATE TABLE Bookings (
	eventID			integer,
	resourceType		resourceType NOT NULL,
	typeID			integer NOT NULL,
	start_at		timestamp with time zone NOT NULL,
	end_at			timestamp with time zone NOT NULL,
	cost			numeric(16,2) DEFAULT 0.00 NOT NULL,
	num			integer NOT NULL,
	description		varchar(256),
	PRIMARY KEY (eventID, resourceType, typeID),
	FOREIGN KEY (eventID) REFERENCES Events(eventID) ON DELETE CASCADE,
	FOREIGN KEY (resourceType,typeID) REFERENCES Resources(resourceType,typeID) ON DELETE CASCADE
);

CREATE TABLE Resources_Require (
	r1resourceType		resourceType,
	r1typeID		integer,
	r2resourceType		resourceType,
	r2typeID		integer,
	numRequired		integer NOT NULL,
	specification		varchar(256),
	PRIMARY KEY (r1resourceType, r1typeID, r2resourceType , r2typeID),
	FOREIGN KEY (r1resourceType, r1typeID) references Resources(resourceType, typeID) ON DELETE CASCADE,
	FOREIGN KEY (r2resourceType, r2typeID) references Resources(resourceType, typeID) ON DELETE CASCADE
);

CREATE TYPE contentRating AS ENUM ('G','PG','PG-13','R','X');

CREATE TABLE Resources_Entertainment(
	resourceType		resourceType NOT NULL,
	typeID			integer NOT NULL,
	name			varchar(128) UNIQUE NOT NULL,
	fee			numeric(16,2) DEFAULT 0.00 NOT NULL,
	genre			varchar(64) NOT NULL,
	contentRating		contentRating NOT NULL,
	spaceRequired		integer,
	PRIMARY KEY (typeID),
	FOREIGN KEY (resourceType, typeID) REFERENCES resources(resourceType, typeID) ON DELETE CASCADE
);

CREATE TABLE Resources_Equipment (
	resourceType		resourceType NOT NULL,
	typeID			integer NOT NULL,
	name			varchar(128) NOT NULL,
	fee			numeric(16,2) DEFAULT 0.00 NOT NULL,
	equipmentType		varchar(128) NOT NULL,
	quantity		integer NOT NULL,
	vendor			varchar(128),
	PRIMARY KEY (typeID),
	FOREIGN KEY (resourceType, typeID) REFERENCES resources(resourceType, typeID) ON DELETE CASCADE
);

CREATE TABLE Resources_Venues (
	resourceType		resourceType NOT NULL,
	typeID			integer NOT NULL,
	name			varchar(128) UNIQUE,
	fee			numeric(16,2) DEFAULT 0.00 NOT NULL,
	address			varchar(128) NOT NULL,
	roomNum			varchar(32),
	capacity		integer DEFAULT 0 NOT NULL,
	stageArea		integer,
	liquorLicense		boolean DEFAULT false,
	PRIMARY KEY (typeID),
	FOREIGN KEY (resourceType, typeID) REFERENCES resources(resourceType, typeID) ON DELETE CASCADE
);

CREATE TABLE Resources_Staff (
	resourceType		resourceType NOT NULL,
	typeID			integer NOT NULL,
	fee			numeric(16,2) DEFAULT 0.00 NOT NULL,
	pronoun			varchar(64) NOT NULL,
	first_name		varchar(128) NOT NULL,
	last_name		varchar(128) NOT NULL,
	email			varchar(128) UNIQUE NOT NULL,
	PRIMARY KEY (typeID),
	FOREIGN KEY (resourceType, typeID) REFERENCES resources(resourceType, typeID) ON DELETE CASCADE

);

CREATE TYPE qualification AS ENUM ('Electrical','Bartending','Serving','Security');

CREATE TABLE Qualifications_Have (
	staff_email		varchar(128) NOT NULL,
	qualification		qualification,
	PRIMARY KEY (staff_email, qualification),
	FOREIGN KEY (staff_email) REFERENCES Resources_Staff(email) ON DELETE CASCADE
);

CREATE TABLE Resources_Caterers (
	resourceType		resourceType NOT NULL,
	typeID			integer NOT NULL,
	name			varchar(128) UNIQUE NOT NULL,
	fee			numeric(16,2) DEFAULT 0.00 NOT NULL,
	PRIMARY KEY (typeID),
	FOREIGN KEY (resourceType, typeID) REFERENCES resources(resourceType, typeID) ON DELETE CASCADE
);

CREATE TABLE Menus_Offered (
	menuID		SERIAL UNIQUE,
	caterer_name	varchar(128) NOT NULL,
	name		varchar(128),
	description	text,
	PRIMARY KEY (menuID, caterer_name),
	FOREIGN KEY (caterer_name) REFERENCES Resources_Caterers(name)
);

CREATE TABLE Menus_Accommodate (
	accomodation	varchar(128),
	menuID		integer,
	caterer_name	varchar(128),
	PRIMARY KEY (accomodation, caterer_name, menuID),
	FOREIGN KEY (menuID) REFERENCES Menus_Offered(menuID) ON DELETE CASCADE,
	FOREIGN KEY (caterer_name) REFERENCES Resources_Caterers(name)
);

