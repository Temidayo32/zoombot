from flask import Flask, request
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from meeting import join_zoom_meeting
from state import in_meeting
import time
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pytz
import asyncio


load_dotenv()

CLIENT_ID = os.getenv('clientID')
CLIENT_SECRET = os.getenv('clientSecret')
REDIRECT_URI = 'http://localhost:5000/callback'
AUTH_URL= os.getenv('authURI')
USER_NAME = "Meeting Bot"


app = Flask(__name__)

access_token = None
refresh_token = None
expires_at = None

@app.route('/callback')
def callback():
    global access_token, refresh_token, expires_at
    authorization_code = request.args.get('code')
    if authorization_code:
        # print(authorization_code)
        access_token_response = get_access_token(authorization_code)
        if access_token_response.get('access_token'):
            access_token = access_token_response['access_token']
            refresh_token = access_token_response['refresh_token']
            expires_in = access_token_response['expires_in']
            expires_at = expires_in + time.time()
            return f'<h1>Authorization Successful</h1><p>Access Token: {access_token}</p>'
        else:
            return '<h1>Failed to retrieve access token</h1>'
    return '<h1>Authorization Failed</h1>'

def refresh_access_token():
    global access_token, refresh_token, expires_at

    # Check if the token is about to expire
    if expires_at and time.time() >= expires_at - 60:  # Refresh 1 minute before expiry
        url = "https://zoom.us/oauth/token"
        client_id = CLIENT_ID
        client_secret = CLIENT_SECRET
        
        response = requests.post(
            url,
            headers={'Authorization': f'Basic {client_id}:{client_secret}'},
            data={
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }
        )

        
        if response.status_code == 200:
            tokens = response.json()
            access_token = tokens['access_token']
            refresh_token = tokens['refresh_token']
            expires_in = tokens['expires_in']

            # Update expiration time
            expires_at = time.time() + expires_in
            print("Token refreshed successfully.")
        else:
            print("Failed to refresh token:", response.text)

def get_access_token(authorization_code):
    url = 'https://zoom.us/oauth/token'
    data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': REDIRECT_URI,
    }
    response = requests.post(url, auth=(CLIENT_ID, CLIENT_SECRET), data=data)
    return response.json()

# Function to check for scheduled meetings
async def check_meetings():
    global in_meeting
    if in_meeting:
        print("Bot is already in a meeting. Waiting for the meeting to finish.")
        return
    meetings = fetch_upcoming_meetings()
    for meeting in meetings:
        if should_join_meeting(meeting, access_token=access_token):
            in_meeting = True
            meeting_status=await join_zoom_meeting(meeting['join_url'], USER_NAME)
            in_meeting = meeting_status
            break
            # driver.quit()

def fetch_upcoming_meetings():
    # Logic to fetch meetings using Zoom API
    response = requests.get(
        "https://api.zoom.us/v2/users/me/meetings",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    # print(response.text)
    return response.json().get('meetings', [])

def check_meeting_status(meeting_id, access_token):
    """Poll Zoom API to check if the meeting has started."""
    url = f"https://api.zoom.us/v2/meetings/{meeting_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        meeting_details = response.json()
        return meeting_details.get('status') == 'started'  # True if the meeting is started
    else:
        print(f"Error: {response.json()}")
        return False

def should_join_meeting(meeting, access_token):
    meeting_start_time = datetime.strptime(meeting['start_time'], "%Y-%m-%dT%H:%M:%SZ")
    meeting_start_time = meeting_start_time.replace(tzinfo=pytz.UTC)
    current_time = datetime.now(pytz.UTC)
    join_window = timedelta(minutes=5)

    if meeting_start_time - join_window <= current_time <= meeting_start_time + timedelta(minutes=100):
        print("Bot waiting to join the meeting. It's time!")

        # Polling the Zoom API to check if the meeting has started
        while True:
            meeting_started = check_meeting_status(meeting['id'], access_token)
            if meeting_started:
                return True  # Meeting has started, the bot can join
            else:
                print("Meeting not started yet. Bot is waiting...")
                time.sleep(30)  # Wait 30 seconds before checking again
    else:
        print("It's not time to join the meeting yet.")
        return False

def schedule_check():
    asyncio.run(check_meetings())

scheduler = BackgroundScheduler()
scheduler.add_job(schedule_check, 'interval', minutes=1, max_instances=3, coalesce=True, misfire_grace_time=60)
scheduler.add_job(refresh_access_token, 'interval', minutes=1, max_instances=3, coalesce=True, misfire_grace_time=60)
scheduler.start()

@app.route('/')
def index():
    return f'<h1>Zoom Bot</h1><a href="{AUTH_URL}">Authorize Zoom App</a>'

if __name__ == "__main__":
    app.run(debug=True)
