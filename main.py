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

async def validate_token(request):
    try:
        id_token = request.cookies.get("token")
        if not id_token:
            return None
        return google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
    except (TransportError, InvalidValue) as e:
        print(f"Error: {e}")
        return None

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    is_logged_in = await validate_token(request)
    drivers = db.collection('drivers').stream()
    teams = db.collection('teams').stream()

    driver_list = [{**driver.to_dict(), "id": driver.id} for driver in drivers]
    team_list = [{**team.to_dict(), "id": team.id} for team in teams]

    return templates.TemplateResponse('index.html', {
        'request': request,
        'drivers': driver_list,
        'teams': team_list,
        'is_logged_in': is_logged_in
    })

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    if request.method == "POST":
        id_token = (await request.form()).get("id_token")
        if id_token:
            response = templates.TemplateResponse('index.html', {'request': request})
            response.set_cookie(key="token", value=id_token)
            return response
    return templates.TemplateResponse('login.html', {'request': request})

@app.get("/view_driver", response_class=HTMLResponse)
async def view_driver(request: Request):
    is_logged_in = await validate_token(request)
    drivers = db.collection('drivers').stream()
    driver_list = [{**driver.to_dict(), "id": driver.id} for driver in drivers]
    return templates.TemplateResponse('view_driver.html', {
        'request': request,
        'drivers': driver_list,
        'is_logged_in': is_logged_in
    })

@app.post("/delete_driver/{driver_id}")
async def delete_driver(driver_id: str, request: Request):
    if not await validate_token(request):
        raise HTTPException(status_code=403, detail="User not authenticated")

    db.collection('drivers').document(driver_id).delete()
    return RedirectResponse("/view_driver", status_code=303)

@app.get("/add_driver", response_class=HTMLResponse)
async def add_team(request: Request):
    if not await validate_token(request):
        raise HTTPException(status_code=403, detail="User not authenticated")

    return templates.TemplateResponse('add_driver.html', {'request': request})

@app.post("/add_driver")
async def add_driver(request: Request):
    if not await validate_token(request):
        raise HTTPException(status_code=403, detail="User not authenticated")

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
    return {"message": "Driver added successfully!"}

@app.get("/driver_details", response_class=HTMLResponse)
async def driver_details(request: Request):
    is_logged_in = await validate_token(request)
    driver_id = request.query_params.get("id")
    if not driver_id:
        raise HTTPException(status_code=400, detail="Driver ID not provided")

    driver_ref = db.collection('drivers').document(driver_id)
    driver = driver_ref.get()

    if not driver.exists:
        raise HTTPException(status_code=404, detail="Driver not found")

    driver_data = {**driver.to_dict(), "id": driver.id}
    return templates.TemplateResponse('driver_details.html', {
        'request': request,
        'is_logged_in': is_logged_in,
        'driver': driver_data
    })

@app.get("/edit_driver", response_class=HTMLResponse)
async def edit_driver(request: Request):
    driver_id = request.query_params.get("id")
    driver_ref = db.collection('drivers').document(driver_id)
    driver = driver_ref.get()
    if not driver.exists:
        raise HTTPException(status_code=404, detail="Driver not found")

    driver_data = driver.to_dict()
    driver_data["id"] = driver.id 
    return templates.TemplateResponse('edit_driver.html', {
        'request': request,
        'driver': driver_data
    })

@app.post("/edit_driver/{driver_id}")
async def edit_driver(driver_id: str, request: Request):
    try:
        if not await validate_token(request):
            raise HTTPException(status_code=403, detail="User not authenticated")

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

            
        db.collection('drivers').document(driver_id).update(driver_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error updating driver information")

    return {"message": "Driver updated successfully!"}

@app.post("/query_driver")
async def query_driver(request: Request):
    # Read parameters from form data
    form_data = await request.form()
    attribute = form_data.get("attribute")
    comparison = form_data.get("comparison")
    value = form_data.get("value")

    if not attribute or not comparison or not value:
        return JSONResponse(content={"error": "Missing parameters"}, status_code=400)

    # Convert value to number if applicable
    try:
        value = int(value)
    except ValueError:
        pass  # Keep as string if conversion fails

    # Map comparison symbols to Firestore operators
    comparison_operators = {
        "=": "==",
        "<": "<",
        ">": ">"
    }
    # Validate comparison operator
    if comparison not in comparison_operators:
        return JSONResponse(content={"error": "Invalid comparison operator"}, status_code=400)

    # Build Firestore query based on the provided parameters
    driver_ref = db.collection("drivers")
    query = driver_ref.where(attribute, comparison_operators[comparison], value)

    # Fetch results
    results = query.stream()
    drivers = [{"id": doc.id, **doc.to_dict()} for doc in results]
    return templates.TemplateResponse('view_driver.html', {
        'request': request,
        'drivers': drivers
    })


@app.get("/view_team", response_class=HTMLResponse)
async def view_team(request: Request):
    is_logged_in = await validate_token(request)
    teams = db.collection('teams').stream()
    team_list = [{**team.to_dict(), "id": team.id} for team in teams]
    
    return templates.TemplateResponse('view_team.html', {
        'request': request,
        'teams': team_list,
        'is_logged_in': is_logged_in
    })

@app.get("/add_team", response_class=HTMLResponse)
async def add_team(request: Request):
    if not await validate_token(request):
        raise HTTPException(status_code=403, detail="User not authenticated")

    return templates.TemplateResponse('view_driver.html', {'request': request})

@app.post("/add_team")
async def add_team_post(request: Request):
    if not await validate_token(request):
        raise HTTPException(status_code=403, detail="User not authenticated")

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
    return {"message": "Team added successfully!"}

@app.get("/compare_drivers", response_class=HTMLResponse)
async def compare_drivers(request: Request):
    driver1_id = request.query_params.get("driver1")
    driver2_id = request.query_params.get("driver2")

    driver1 = db.collection("drivers").document(driver1_id).get().to_dict()
    driver2 = db.collection("drivers").document(driver2_id).get().to_dict()

    return templates.TemplateResponse('compare_drivers.html', {
        'request': request,
        'driver1': driver1,
        'driver2': driver2
    })

@app.get("/compare_teams", response_class=HTMLResponse)
async def compare_teams(request: Request):
    return templates.TemplateResponse('compare_teams.html', {'request': request})
