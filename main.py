from fastapi import FastAPI, Request, Form, HTTPException
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

async def validate_token(request: Request):
    id_token = request.cookies.get("token")
    user_token = None

    if id_token:
        try:
            user_token = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError as err:
            print(str(err))

    return user_token is not None

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # Validate the token to check if the user is logged in
    is_logged_in = await validate_token(request)
    # Fetch driver and team data
    drivers = db.collection('drivers').stream()
    teams = db.collection('teams').stream()

    driver_list = [{**driver.to_dict(), "id": driver.id} for driver in drivers]
    team_list = [{**team.to_dict(), "id": team.id} for team in teams]

    # Return the index page regardless of login status, but disable modification buttons if not logged in
    return templates.TemplateResponse('index.html', {
        'request': request,
        'drivers': driver_list,
        'teams': team_list,
        'is_logged_in': is_logged_in
    })


@app.api_route("/add_driver", methods=["GET", "POST"])
async def add_driver(request: Request):
    if request.method == "GET":
        return templates.TemplateResponse('add_driver.html', {'request': request})
    if not await validate_token(request):
        raise HTTPException(status_code=403, detail="User not authenticated")

    form = await request.form()
    name = form.get("name")
    age = form.get("age")
    total_pole_positions = form.get("total_pole_positions")
    total_race_wins = form.get("total_race_wins")
    total_points = form.get("total_points")
    total_world_titles = form.get("total_world_titles")
    total_fastest_laps = form.get("total_fastest_laps")
    team = form.get("team")
    driver_data = {
        "name": name,
        "age": age,
        "total_pole_positions": total_pole_positions,
        "total_race_wins": total_race_wins,
        "total_points": total_points,
        "total_world_titles": total_world_titles,
        "total_fastest_laps": total_fastest_laps,
        "team": team
    }
    db.collection('drivers').add(driver_data)
    return {"message": "Driver added successfully!"}

@app.delete("/delete_driver/{driver_id}")
async def delete_driver(driver_id: str, request: Request):
    if not await validate_token(request):
        raise HTTPException(status_code=403, detail="User not authenticated")

    db.collection('drivers').document(driver_id).delete()
    return {"message": "Driver deleted successfully!"}

@app.api_route("/login", methods=["GET", "POST"], response_class=HTMLResponse)
async def login(request: Request):
    if request.method == "POST":
        id_token = (await request.form()).get("id_token")
        if id_token:
            # Verify the token and set the cookie
            response = templates.TemplateResponse('index.html', {'request': request})
            response.set_cookie(key="token", value=id_token)
            return response
    return templates.TemplateResponse('login.html', {'request': request})

@app.api_route("/add_team", methods=["GET", "POST"])
async def add_team(request: Request):
    if request.method == "GET":
        return templates.TemplateResponse('add_team.html', {'request': request})
    if not await validate_token(request):
        raise HTTPException(status_code=403, detail="User not authenticated")

    form = await request.form()
    team_name = form.get("team_name")
    year_founded = form.get("year_founded")
    total_pole_positions = form.get("total_pole_positions")
    total_race_wins = form.get("total_race_wins")
    total_constructor_titles = form.get("total_constructor_titles")
    finishing_position = form.get("finishing_position")
    team_data = {
        "team_name": team_name,
        "year_founded": year_founded,
        "total_pole_positions": total_pole_positions,
        "total_race_wins": total_race_wins,
        "total_constructor_titles": total_constructor_titles,
        "finishing_position": finishing_position
    }
    db.collection('teams').add(team_data)
    return {"message": "Team added successfully!"}

@app.get("/compare_drivers", response_class=HTMLResponse)
async def compare_drivers(request: Request):
    return templates.TemplateResponse('compare_drivers.html', {'request': request})

@app.get("/compare_teams", response_class=HTMLResponse)
async def compare_teams(request: Request):
    return templates.TemplateResponse('compare_teams.html', {'request': request})

# Additional routes and logic can be added here as needed.
