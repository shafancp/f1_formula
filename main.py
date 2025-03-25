from fastapi import FastAPI, Request, Form, HTTPException 
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.oauth2.id_token
from google.auth.transport import requests
from google.cloud import firestore
from google.auth.exceptions import TransportError, InvalidValue
from google.cloud.firestore_v1.base_query import FieldFilter


# Define the app
app = FastAPI()

# Firebase request adapter
firebase_request_adapter = requests.Request()
db = firestore.Client()

# Define static and templates directories
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory="templates")

#function that we will use to validate an id_token. will return the user_token if valid, None if not
def validateFirebaseToken(id_token):
    if not id_token:
        return False  # or None
    try:
        google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        return True
    except ValueError as err:  
        print(f"Token validation error: {err}")
        return False

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    id_token = request.cookies.get("token")
    is_logged_in = validateFirebaseToken(id_token)
    return templates.TemplateResponse('index.html', {'request': request,'is_logged_in': is_logged_in})

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    if request.method == "POST":
        id_token = request.cookies.get("token")
        is_logged_in = validateFirebaseToken(id_token)
        if is_logged_in:
            response = templates.TemplateResponse('index.html', {'request': request})
            return response
    return templates.TemplateResponse('login.html', {'request': request, 'error': 'Invalid token'})

@app.get("/view_driver", response_class=HTMLResponse)
async def view_driver(request: Request):
    id_token = request.cookies.get("token")
    is_logged_in = validateFirebaseToken(id_token)
    drivers = db.collection('drivers').stream()
    driver_list = [{**driver.to_dict(), "id": driver.id} for driver in drivers]
    return templates.TemplateResponse('view_driver.html', {'request': request, 'drivers': driver_list, 'is_logged_in': is_logged_in})

@app.get("/delete_driver")
async def delete_driver(request: Request):
    driver_id = request.query_params.get("id")
    id_token = request.cookies.get("token")
    is_logged_in = validateFirebaseToken(id_token)
    if not is_logged_in:
        return templates.TemplateResponse('login.html', {'request': request})
    db.collection('drivers').document(driver_id).delete()
    return RedirectResponse("/view_driver", status_code=303)

@app.get("/add_driver", response_class=HTMLResponse)
async def add_driver(request: Request):
    id_token = request.cookies.get("token")
    is_logged_in = validateFirebaseToken(id_token)
    if not is_logged_in:
        return templates.TemplateResponse('login.html', {'request': request})
    teams = db.collection('teams').stream()
    team_list = [{**team.to_dict(), "id": team.id} for team in teams]
    return templates.TemplateResponse('add_driver.html', {'request': request, 'teams' : team_list})

@app.post("/add_driver")
async def add_driver(request: Request):
    form = await request.form()
    driver_data = {
        "name": form.get("name"),
        "age": form.get("age"),
        "total_pole_positions": form.get("total_pole_positions"),
        "total_race_wins": form.get("total_race_wins"),
        "total_points": form.get("total_points"),
        "total_world_titles": form.get("total_world_titles"),
        "total_fastest_laps": form.get("total_fastest_laps"),
        "team": form.get("team")
    }
    db.collection('drivers').add(driver_data)
    return HTMLResponse("""<script> alert("Added Driver successfully!"); window.location.href = "/view_driver"; </script> """)

@app.get("/driver_details", response_class=HTMLResponse)
async def driver_details(request: Request):
    id_token = request.cookies.get("token")
    is_logged_in = validateFirebaseToken(id_token)
    driver_id = request.query_params.get("id")
    driver_ref = db.collection('drivers').document(driver_id)
    driver = driver_ref.get()
    driver_data = {**driver.to_dict(), "id": driver.id, "team_name": None}
    team_id = driver_data.get("team")
    team_data = db.collection('teams').document(team_id).get().to_dict()
    driver_data["team_name"] = team_data.get("team_name") if team_data else "Unknown Team"
    return templates.TemplateResponse('driver_details.html', {'request': request, 'is_logged_in': is_logged_in, 'driver': driver_data })

@app.get("/edit_driver", response_class=HTMLResponse)
async def edit_driver(request: Request):
    id_token = request.cookies.get("token")
    is_logged_in = validateFirebaseToken(id_token)
    if not is_logged_in:
        return templates.TemplateResponse('login.html', {'request': request})
    driver_id = request.query_params.get("id")
    driver_ref = db.collection('drivers').document(driver_id)
    driver = driver_ref.get()
    driver_data = driver.to_dict()
    driver_data["id"] = driver.id 
    teams = db.collection('teams').stream()
    team_list = [{**team.to_dict(), "id": team.id} for team in teams]
    return templates.TemplateResponse('edit_driver.html', {'request': request, 'driver': driver_data, 'teams': team_list})

@app.post("/edit_driver")
async def edit_driver(request: Request):
    form = await request.form()
    driver_id = form.get("id")
    driver_data = {
        "name": form.get("name"),
        "age": form.get("age"),
        "total_pole_positions": form.get("total_pole_positions"),
        "total_race_wins": form.get("total_race_wins"),
        "total_points": form.get("total_points"),
        "total_world_titles": form.get("total_world_titles"),
        "total_fastest_laps": form.get("total_fastest_laps"),
        "team": form.get("team")
        }

    db.collection('drivers').document(driver_id).update(driver_data)
    return RedirectResponse(url=f"/driver_details?id={driver_id}", status_code=303)

@app.get("/filter_driver", response_class=HTMLResponse)
async def get_filter_driver(request: Request):
    drivers = db.collection('drivers').stream()
    driver_list = [{**driver.to_dict(), "id": driver.id} for driver in drivers]
    return templates.TemplateResponse('filter_driver.html', {'request': request, 'drivers': driver_list })
    

@app.post("/filter_driver")
async def filter_driver(request: Request):
    form_data = await request.form()
    attribute = form_data.get("attribute")
    comparison = form_data.get("comparison")
    value = form_data.get("value")
    drivers_ref = db.collection("drivers")
    query = drivers_ref.where(attribute, comparison, value)
    drivers = query.stream()
    driver_list = [{**driver.to_dict(), "id": driver.id} for driver in drivers]
    return templates.TemplateResponse('filter_driver.html', {'request': request, 'drivers': driver_list})


@app.get("/view_team", response_class=HTMLResponse)
async def view_team(request: Request):
    id_token = request.cookies.get("token")
    is_logged_in = validateFirebaseToken(id_token)
    teams = db.collection('teams').stream()
    team_list = [{**team.to_dict(), "id": team.id} for team in teams]
    return templates.TemplateResponse('view_team.html', {'request': request, 'teams': team_list, 'is_logged_in': is_logged_in })

@app.get("/add_team", response_class=HTMLResponse)
async def add_team(request: Request):
    id_token = request.cookies.get("token")
    is_logged_in = validateFirebaseToken(id_token)
    if not is_logged_in:
        return templates.TemplateResponse('login.html', {'request': request})

    return templates.TemplateResponse('add_team.html', {'request': request})

@app.post("/add_team")
async def add_team_post(request: Request):
    id_token = request.cookies.get("token")
    is_logged_in = validateFirebaseToken(id_token)
    if not is_logged_in:
        return templates.TemplateResponse('login.html', {'request': request})

    form = await request.form()
    team_data = {
        "team_name": form.get("team_name"),
        "year_founded": form.get("year_founded"),
        "total_pole_positions": form.get("total_pole_positions"),
        "total_race_wins": form.get("total_race_wins"),
        "total_constructor_titles": form.get("total_constructor_titles"),
        "finishing_position": form.get("finishing_position")
    }
    db.collection('teams').add(team_data)
    return HTMLResponse("""<script> alert("Added Driver successfully!"); window.location.href = "/view_team"; </script> """)

@app.get("/compare_drivers", response_class=HTMLResponse)
async def compare_drivers_get(request: Request):
    drivers = db.collection('drivers').stream()
    driver_list = [{**driver.to_dict(), "id": driver.id} for driver in drivers]
    return templates.TemplateResponse('compare_drivers.html', {'request': request, 'drivers': driver_list })

@app.post("/compare_drivers", response_class=HTMLResponse)
async def compare_drivers_post(request: Request):
    form_data = await request.form()
    driver1_id = form_data.get("driver1")
    driver2_id = form_data.get("driver2")

    driver1 = db.collection("drivers").document(driver1_id).get().to_dict()
    driver2 = db.collection("drivers").document(driver2_id).get().to_dict()
    drivers = db.collection('drivers').stream()
    driver_list = [{**driver.to_dict(), "id": driver.id} for driver in drivers]

    return templates.TemplateResponse('compare_drivers.html', {
        'request': request,
        'driver1': driver1,
        'driver2': driver2,
        'drivers': driver_list
    })

@app.get("/compare_teams", response_class=HTMLResponse)
async def compare_teams(request: Request):
    team1_id = request.query_params.get("team1")
    team2_id = request.query_params.get("team2")

    team1 = db.collection("teams").document(team1_id).get().to_dict()
    team2 = db.collection("teams").document(team2_id).get().to_dict()

    return templates.TemplateResponse('compare_teams.html', {
        'request': request,
        'team1': team1,
        'team2': team2
    })
