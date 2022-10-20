#!/usr/bin/python3

import datetime
import os.path
import sys

try:
    from googleapiclient import discovery
    from googleapiclient.http import build_http
except ImportError as e:
    print(f"{e}\n\nPlease try apt install python3-googleapi")
    sys.exit(1)
try:
    from oauth2client import (
        client,
        file,
        tools,
    )
except ImportError as e:
    print(f"{e}\n\nPlease try apt install python3-oauth2client")
    sys.exit(1)


def print_setup_credentials_help():
    print(
        """
No credentials found in {}

Please enable the calendar API and create a credentials file.

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
""".format(
            config["credentials_path"]
        )
    )


# snapd calendar
default_calendar_id = "michael.vogt@canonical.com"
# use checkout dir of the code to store credentials (for convenience)
default_credentials_path = os.path.join(
    os.path.dirname(sys.argv[0]), "credentials.json"
)

config = {
    "calendar_id": os.environ.get("CLEARCAL_CALENDAR_ID", default_calendar_id),
    "credentials_path": os.environ.get(
        "CLEARCAL_CREDENTIALS_PATH", default_credentials_path
    ),
}


def collect_my_events(http, date):
    date_min = date + "T00:00:00Z"
    date_max = date + "T23:59:00Z"
    service = discovery.build("calendar", "v3", http=http)
    events = (
        service.events()
        .list(
            calendarId=config["calendar_id"],
            timeMin=date_min,
            timeMax=date_max,
            maxResults=50,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    items = []
    for item in events["items"]:
        if item["creator"].get("self", False):
            items.append(item)
    return items


def del_events(http, events):
    service = discovery.build("calendar", "v3", http=http)
    for event in events:
        print("deleting", event["summary"])
        service.events().delete(
            calendarId=config["calendar_id"], eventId=event["id"]
        ).execute()


def main(argv):
    if not os.path.exists(config["credentials_path"]):
        print_setup_credentials_help()
        return False

    if len(sys.argv) < 2:
        print("need a date to delete events")
        return False

    # add cmdline to get the date
    date = sys.argv[1]

    # Authenticate and construct service.
    credentials = config["credentials_path"]
    scope = "https://www.googleapis.com/auth/calendar.events"
    flow = client.flow_from_clientsecrets(
        credentials, scope=scope, message=tools.message_if_missing(credentials)
    )
    storage = file.Storage("calendar.dat")
    credentials = storage.get()
    flags = None
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, storage, flags)
    http = credentials.authorize(http=build_http())

    events = collect_my_events(http, date)
    print(f"Events for {date}:")
    for event in events:
        start = (
            datetime.datetime.fromisoformat(event["start"]["dateTime"])
            .time()
            .isoformat(timespec="minutes")
        )
        end = (
            datetime.datetime.fromisoformat(event["end"]["dateTime"])
            .time()
            .isoformat(timespec="minutes")
        )
        print(f""" {start}-{end}  {event["summary"]}""")
    print("Delete all events? [yN]", end="", flush=True)
    yes_no = sys.stdin.readline()
    if yes_no.strip() == "y":
        del_events(http, events)
    return True


if __name__ == "__main__":
    if not main(sys.argv):
        sys.exit(1)
