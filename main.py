from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.oauth2.id_token
from google.auth.transport import requests

# Define the app
app = FastAPI()

# Firebase request adapter
firebase_request_adapter = requests.Request()
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

    return templates.TemplateResponse('login.html', {'request': request, 'user_token': user_token, 'error_message': error_message})


