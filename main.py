from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.oauth2.id_token
from google.auth.transport import requests
from google.cloud import firestore

# Define the app
app = FastAPI()

# Firebase request adapter
firebase_request_adapter = requests.Request()
db = firestore.Client()

# Define static and templates directories
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # Query Firebase for the request token
    id_token = request.cookies.get("token")
    error_message = "No error here"
    user_token = None

    # Verify the ID token
    if id_token:
        try:
            user_token = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError as err:
            # Log the error and update the error message for the template
            print(str(err))

    if user_token:
        return templates.TemplateResponse('index.html', {'request': request, 'user_token': user_token})
    else:
        return templates.TemplateResponse('login.html', {'request': request, 'user_token': user_token, 'error_message': error_message})

@app.get("/compare_drivers", response_class=HTMLResponse)
async def compare_drivers(request: Request):
    # Logic to compare drivers and display their stats
    return templates.TemplateResponse('compare_drivers.html', {'request': request})

@app.get("/compare_teams", response_class=HTMLResponse)
async def compare_teams(request: Request):
    # Logic to compare teams and display their stats
    return templates.TemplateResponse('compare_teams.html', {'request': request})

# Additional routes and logic can be added here as needed.
