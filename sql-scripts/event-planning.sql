DROP TABLE events CASCADE;
DROP TABLE event_planners;
DROP TABLE Bookings CASCADE;
DROP TABLE guests_attend CASCADE;
DROP TABLE dietary_restrictions_have CASCADE;
DROP TABLE dietary_restrictions_accommodate CASCADE;
DROP TABLE dietary_restrictions_match CASCADE;
DROP TABLE resources_require;
DROP TABLE resources CASCADE;
DROP TABLE qualifications_have;
DROP TYPE qualification;
DROP TYPE contentRating;
DROP TYPE resourceType;


CREATE TABLE Event_Planners (
	plannerID		SERIAL PRIMARY KEY,
	name			varchar(128) NOT NULL,
	email			varchar(128) UNIQUE NOT NULL,
	phone			varchar(128) NOT NULL,
	pronoun			varchar(16) NOT NULL
);

CREATE TABLE Events (
	eventID			SERIAL PRIMARY KEY,
	date			date NOT NULL,
	start_at		timestamp with time zone NOT NULL,
	end_at			timestamp with time zone NOT NULL,
	location		varchar(128) NOT NULL,
	cost			numeric(16,2) DEFAULT 0.00 NOT NULL,
	budget			numeric(16,2) DEFAULT 0.00 NOT NULL,
	planned_by		integer NOT NULL,
	event_name		varchar(128) NOT NULL,
	over_21			boolean DEFAULT false,
	FOREIGN KEY (planned_by) REFERENCES Event_Planners (plannerID)
);

CREATE TABLE Guests_Attend (
	eventID			integer,
	email			varchar(128) UNIQUE,
	title			varchar(128) NOT NULL,
	name			varchar(128) NOT NULL,
	phone			varchar(32) NOT NULL,
	pronoun			varchar(16) NOT NULL,
	under_21		boolean DEFAULT false,
	PRIMARY KEY (eventID,email),
	FOREIGN KEY (eventID) REFERENCES Events(eventID) ON DELETE CASCADE
);

CREATE TYPE resourceType AS ENUM ('Entertainment', 'Equipment', 'Venues','Staff','Caterers');

CREATE TABLE Resources (
	resourceID		SERIAL UNIQUE,
	resourceType		resourceType NOT NULL,
	name			varchar(128) NOT NULL,
	num			integer NOT NULL,
	fee			numeric(16,2) DEFAULT 0.00 NOT NULL,
	specification		varchar(256),
	PRIMARY KEY (resourceID)
);

CREATE TABLE Bookings (
	eventID			integer,
	resourceID		integer,
	start_at		timestamp with time zone NOT NULL,
	end_at			timestamp with time zone NOT NULL,
	cost			numeric(16,2) DEFAULT 0.00 NOT NULL,
	num			integer NOT NULL,
	description		varchar(256),
	PRIMARY KEY (eventID, resourceID),
	FOREIGN KEY (eventID) REFERENCES Events(eventID) ON DELETE CASCADE,
	FOREIGN KEY (resourceID) REFERENCES Resources(resourceID) ON DELETE CASCADE
);

CREATE TABLE Resources_Require (
	resourceID1		integer,
	resourceID2		integer,
	numRequired		integer NOT NULL,
	specification		varchar(256),
	PRIMARY KEY (resourceID1, resourceID2),
	FOREIGN KEY (resourceID1) references Resources(resourceID),
	FOREIGN KEY (resourceID2) references Resources(resourceID)
);

CREATE TYPE contentRating AS ENUM ('G','PG','PG-13','R','X');

CREATE TABLE Resources_Entertainment(
	genre			varchar(64) NOT NULL,
	contentRating		contentRating NOT NULL,
	spaceRequired		integer,
	PRIMARY KEY (resourceID),
	FOREIGN KEY (resourceID) REFERENCES Resources(resourceID)
) INHERITS (Resources);

CREATE TABLE Resources_Equipment (
	equipmentType		varchar(128) NOT NULL,
	quantity		integer NOT NULL,
	vendor			varchar(128),
	PRIMARY KEY (resourceID),
	FOREIGN KEY (resourceID) REFERENCES Resources(resourceID)
) INHERITS (Resources);

CREATE TABLE Resources_Venues (
	address			varchar(128) NOT NULL,
	roomNum			varchar(32),
	capacity		integer DEFAULT 0 NOT NULL,
	stageArea		integer,
	liquorLicense		boolean DEFAULT false,
	PRIMARY KEY (resourceID),
	FOREIGN KEY (resourceID) REFERENCES Resources(resourceID)
) INHERITS (Resources);

CREATE TABLE Resources_Staff (
	pronoun			varchar(16) NOT NULL,
	PRIMARY KEY (resourceID),
	FOREIGN KEY (resourceID) REFERENCES Resources(resourceID)
) INHERITS (Resources);

CREATE TYPE qualification AS ENUM ('Electrical','Bartending','Serving','Security');

CREATE TABLE Qualifications_Have (
	staffID			integer,
	qualification		qualification,
	PRIMARY KEY (staffID, qualification),
	FOREIGN KEY (staffID) REFERENCES Resources_Staff(resourceID) ON DELETE CASCADE
);

CREATE TABLE Resources_Caterers (
	PRIMARY KEY (resourceID),
	FOREIGN KEY (resourceID) REFERENCES Resources(resourceID) ON DELETE CASCADE 
) INHERITS (Resources);

CREATE TABLE Dietary_Restrictions_Have (
	email		varchar(128),
	restriction	varchar(128),
	severity	varchar(128),
	PRIMARY KEY (email, restriction),
	FOREIGN KEY (email) REFERENCES Guests_Attend(email) ON DELETE CASCADE
);

CREATE TABLE Dietary_Restrictions_Accommodate (
	restriction	varchar(128),
	resourceID	integer,
	PRIMARY KEY (restriction, resourceID),
	FOREIGN KEY (resourceID) REFERENCES Resources_Caterers(resourceID) ON DELETE CASCADE
);

CREATE TABLE Dietary_Restrictions_Match (
	caterer_ID		integer,
	guestEmail		varchar(128),
	guestRestriction	varchar(128),
	PRIMARY KEY (caterer_ID, guestEmail, guestRestriction),
	FOREIGN KEY (guestEmail,guestRestriction) references Dietary_Restrictions_Have(email,restriction),
	FOREIGN KEY (caterer_ID,guestRestriction) REFERENCES Dietary_Restrictions_Accommodate(resourceID,restriction) ON DELETE CASCADE
);	
