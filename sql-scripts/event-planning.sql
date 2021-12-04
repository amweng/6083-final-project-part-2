DROP TABLE events CASCADE;
DROP TABLE event_planners;
DROP TABLE Bookings CASCADE;
DROP TABLE guests_attend CASCADE;
DROP TABLE dietary_restrictions_have CASCADE;
DROP TABLE menus_offered CASCADE;
DROP TABLE menus_accommodate CASCADE;
DROP TABLE resources_require;
DROP TABLE resources CASCADE;
DROP TABLE qualifications_have;
DROP TYPE qualification;
DROP TYPE contentRating;
DROP TYPE resourceType;


CREATE TABLE Event_Planners (
	email			varchar(128) PRIMARY KEY,
	first_name		varchar(128) NOT NULL,
	last_name		varchar(128) NOT NULL,
	phone			varchar(128) NOT NULL,
	pronoun			varchar(16) NOT NULL
);

CREATE TABLE Events (
	eventID			integer PRIMARY KEY,
	date			date NOT NULL,
	start_at		timestamp with time zone NOT NULL,
	end_at			timestamp with time zone NOT NULL,
	location		varchar(128) NOT NULL,
	cost			numeric(16,2) DEFAULT 0.00 NOT NULL,
	budget			numeric(16,2) DEFAULT 0.00 NOT NULL,
	event_planner_email	varchar(128) NOT NULL,
	event_name		varchar(128) NOT NULL,
	over_21			boolean DEFAULT false,
	FOREIGN KEY (event_planner_email) REFERENCES Event_Planners (email)
);

CREATE TABLE Guests_Attend (
	eventID			integer NOT NULL,
	email			varchar(128) UNIQUE,
	title			varchar(128) NOT NULL,
	first_name		varchar(128) NOT NULL,
	last_name		varchar(128) NOT NULL,
	phone			varchar(32) NOT NULL,
	pronoun			varchar(16) NOT NULL,
	under_21		boolean DEFAULT false,
	PRIMARY KEY (eventID,email),
	FOREIGN KEY (eventID) REFERENCES Events(eventID)
);

CREATE TABLE Dietary_Restrictions_Have (
	email		varchar(128),
	restriction	varchar(128),
	severity	varchar(128),
	PRIMARY KEY (email, restriction),
	FOREIGN KEY (email) REFERENCES Guests_Attend(email) ON DELETE CASCADE
);


CREATE TYPE resourceType AS ENUM ('Entertainment', 'Equipment', 'Venues','Staff','Caterers');

CREATE TABLE Resources (
	resourceType		resourceType NOT NULL,
	typeID			integer NOT NULL,
	fee			numeric(16,2) DEFAULT 0.00 NOT NULL,
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
	FOREIGN KEY (r2resourceType, r2typeID) references Resources(resourceType, typeID)
);

CREATE TYPE contentRating AS ENUM ('G','PG','PG-13','R','X');

CREATE TABLE Resources_Entertainment(
	name			varchar(128) UNIQUE NOT NULL,
	genre			varchar(64) NOT NULL,
	contentRating		contentRating NOT NULL,
	spaceRequired		integer,
	PRIMARY KEY (resourceType, typeID),
	FOREIGN KEY (resourceType, typeID) REFERENCES Resources(resourceType, typeID)
) INHERITS (Resources);

CREATE TABLE Resources_Equipment (
	name			varchar(128) NOT NULL,
	equipmentType		varchar(128) NOT NULL,
	quantity		integer NOT NULL,
	vendor			varchar(128),
	PRIMARY KEY (resourceType, typeID),
	FOREIGN KEY (resourceType, typeID) REFERENCES Resources(resourceType, typeID)
) INHERITS (Resources);

CREATE TABLE Resources_Venues (
	name			varchar(128) UNIQUE,
	address			varchar(128) NOT NULL,
	roomNum			varchar(32),
	capacity		integer DEFAULT 0 NOT NULL,
	stageArea		integer,
	liquorLicense		boolean DEFAULT false,
	PRIMARY KEY (resourceType, typeID),
	FOREIGN KEY (resourceType, typeID) REFERENCES Resources(resourceType, typeID)
) INHERITS (Resources);

CREATE TABLE Resources_Staff (
	first_name		varchar(128) NOT NULL,
	last_name		varchar(128) NOT NULL,
	email			varchar(128) UNIQUE NOT NULL,
	pronoun			varchar(16) NOT NULL,
	PRIMARY KEY (resourceType, typeID),
	FOREIGN KEY (resourceType, typeID) REFERENCES Resources(resourceType, typeID)
) INHERITS (Resources);

CREATE TYPE qualification AS ENUM ('Electrical','Bartending','Serving','Security');

CREATE TABLE Qualifications_Have (
	staff_email		varchar(128) NOT NULL,
	qualification		qualification,
	PRIMARY KEY (staff_email, qualification),
	FOREIGN KEY (staff_email) REFERENCES Resources_Staff(email) ON DELETE CASCADE
);

CREATE TABLE Resources_Caterers (
	name			varchar(128) UNIQUE NOT NULL,
	PRIMARY KEY (resourceType, typeID),
	FOREIGN KEY (resourceType, typeID) REFERENCES Resources(resourceType, typeID)
) INHERITS (Resources);

CREATE TABLE Menus_Offered (
	menuID		SERIAL UNIQUE,
	caterer_name	varchar(128) NOT NULL,
	name		varchar(128),
	description	text,
	PRIMARY KEY (menuID, caterer_name),
	FOREIGN KEY (caterer_name) REFERENCES Resources_Caterers(name) ON DELETE CASCADE

);

CREATE TABLE Menus_Accommodate (
	accomodation	varchar(128),
	menuID		integer,
	caterer_name	varchar(128),
	PRIMARY KEY (accomodation, caterer_name, menuID),
	FOREIGN KEY (menuID) REFERENCES Menus_Offered(menuID) ON DELETE CASCADE,
	FOREIGN KEY (caterer_name) REFERENCES Resources_Caterers(name)
);

