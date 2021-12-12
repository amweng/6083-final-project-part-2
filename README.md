# Database-Oriented Event Planning
## Final Project Submission

> Repository created by
> __Andrew Weng__ (aw4108)

> __Russell Wustenberg__ (rw2873)

__CS-GY 6083 - PRINCIPLES OF DATABASE SYSTEMS__

Taught by Professor Julia Stoyonovitch

Fall Semester, 2021

New York University's Tandon School of Engineering 

---

This is the final project submission for Andrew Weng (aw4108) and Russell Wustenberg (rw2873) for the fall 2021 
Principles of Database Systems course at New York University's Tandon School of Engineering.  It was conceived of
and jointly contributed by both parties equally.

---

### Overview of the Application
* Did your wedding photographer show up to the wrong venue on the day of your wedding?
* Did the band that your friend recommend to you turn out to only play Irish synth pop?
* Did you say 'fifty balloons' but your newphew only brought home 'fifteen'?

Anyone who has planned a large gathering knows that the party is always a bit _less_ fun for the party planner! 
Event planners often have to coordinate several separate companies, each with unique rules and requirements. 
We have gathered information on useful resources for you to plan your event, centralizing the booking and 
management experience. This way you can focus on getting to the fun faster!

### What To Look For
When you spin up our webpage, you will find yourself with a 'superuser' view of our application.  There are three
primary flavors for viewing the data:

* Event Planner View,
* Vendor View, and
* CEO View

These represent the three primary agents in the fictional event booking company that we have designed.  They each
have a unique perspective and set of interactions with the data.

NB: CEO view in its current implementation is primarily focused on high-level surveys of the data.  Eventually it
would also include statistics gathering tools and administrative control over the vendor and planner profiles.

### Viewing the Data

Once you have copied this repository into your desired location, it is simple to load in the data and get 
the scripts working using your local python interpreter.  Within `sql-scripts` are two files which will
automatically load in the data from the CSV files in `data`.  From within your postgreSQL database,
you can create and populate the data by running the following two commands:

`\i PATH_TO/sql-scripts/schema.sql`

> This command will run the SQL creation file and set up all of the tables for the database.

`\i PATH_TO/sql-scripts/load-data.sql`

> This command will populate the data with over __2,000__ unique data entries!

### What to do?
Once you are viewing the web page, feel free to play! Plan out an event, make a few bookings, or view the set up
from any of the 33 pre-populated template events!  Just don't send any e-mails to the listed e-mail address! They
are completely fake.

Have fun!
