# myMusicianJournal
___A Database for Focused Musicians___<br>
___Christopher M. LaPonsie___


Prior Learning Assessment Portfolio for CISP 246
Davenport University<br>
A live demo of the app can be found here<br>
https://afternoon-plains-28552.herokuapp.com/<br>
<br>
### How to access
This app has been tested on Ubuntu and Heroku hosting service.  It should theoretically work on windows with minimal changes as well.  
I recommend simply accessing the app at the above link for demo purposes.  If you wish to self-host, it requires Python 3.7+ and the following modules:
- flask
- flask-login
- passlib
### Getting started
If the app isn't used for a period of time, Heroku will shutdown the app.  When it relaunches, the database will be restored to its original state.
For this reason, don't expect your data to persist between sessions.  To get started, go to https://afternoon-plains-28552.herokuapp.com and click 'register'.
You can use any email address as there is no email verification implement.  For example, you can just use test@test.com, and choose whatever you want
for the password.  After submitting, if the passwords match, you will get a message saying registration succeeded.  You can then proceed to login with
those credentials.
### Screens
There are four screens: Summary, Categories, Exercises, and Practice.  After logging in, it will bring you to the Summary screen but it won't have
any details.  This is a bit misleading and is a small bug that happens only immediately after logging.  You can click to the other screens
and then click back to the Summary screen to get the real summary page.
#### Summary
This screen is meant to show an overview of the musicians recent practice sessions.  A radar chart shows how much time the musician is spending
on each category.  These categories are defined by the user in the Categories page.  If a category exists but doesn't have practice sessions associated with it
it will not be displayed on the chart.
#### Categories
This screen shows the custom categories the user has and allows the creation of more categories using the "New Category" form at the bottom of the page.
#### Exercises
This screen shows the custom exercises the user has and allows the creation of more exercises using the "New Exercise" form at the bottom of the page.
Provide an exercise name that will be recognizable to you if you are going to be working on this exercise often.  Select a category; this list is populated
from the categories query for that user_id.  Source_URL is intended to be used to allow the musician to reference the sheet music or learning notes while practicing.
If the URL is valid, it will be displayed in an iframe in the practice screen while the musician is practicing.  UoM defines the criteria by which improvement
can be measured.  Finally, notes is a purely optional field for the musician to record additional information pertaining to the exercise.
#### Practice
This screen creates new rows in the PracticeSession table.  It provides a few creature-comfort features, such as begin/end buttons to assign timestamps for the exercise.
This makes it easier to calculate duration later, as well as provides another field that can be selected for during queries.  The exercise dropdown is populated from the
Exercises table.  When it changes, it submits an HTTP/GET request to the back-end Python Flask app that returns JSON data about the exercises and populates the exercise details 
section of this page.
