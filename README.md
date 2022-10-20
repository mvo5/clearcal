# Simple script to clear own events from a gcalendar

This script will help to clear calendar events when going
to events like the engineering sprints. It will delete all
calendar events for which you are owner. 

The main use-case is the Canonical engineering sprints.


## How to enable

Please enable the calendar API and create a credentials file
and put it next to the script location.

This can be done e.g. via the button on:
https://developers.google.com/calendar/quickstart/python#step_1_turn_on_the
(this will give you a generic "Quickstart" token)

Or enable a custom token via the dashboard:
https://console.developers.google.com/apis/dashboard
- create project
- add calendar API to project
- add oauth client credentials
- downlaod them as "credentials.json"

You can customize the path of the credentials file via the
CLEARCAL_CREDENTIALS_PATH environment variable.

You can customize the calendar to use via the
CLEARCAL_CALENDAR_ID environment variable.

