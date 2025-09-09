# FastAPI Formula 1 App 🏎️

A web application built with **FastAPI** and **Firebase** that allows users to manage and explore Formula 1 drivers and teams. Users can view, add, edit, delete, filter, and compare drivers and teams. The app includes authentication via Firebase tokens to ensure secure access to sensitive operations.

---

## Features

### Authentication
- **`validateFirebaseToken(id_token)`**: Validates a Firebase authentication token.
- **`root(request)`**: Retrieves token from cookies, validates it, and renders the index template.
- **`login(request)`**: Renders the login page.

### Driver Management
- **View Drivers**: `view_driver(request)`  
- **Add Driver**: `add_driver(request)` and `add_driver_post(request)`  
- **Edit Driver**: `edit_driver(request)` and `edit_driver_post(request)`  
- **Delete Driver**: `delete_driver(request)`  
- **Filter Drivers**: `filter_driver(request)` and `filter_driver_post(request)`  
- **View Driver Details**: `driver_details(request)`  
- **Compare Drivers**: `compare_drivers(request)` and `compare_drivers_post(request)`  

### Team Management
- **View Teams**: `view_team(request)`  
- **Add Team**: `add_team(request)`  
- **Edit Team**: `edit_team(request)` and `edit_team_post(request)`  
- **Delete Team**: `delete_team(request)`  
- **Filter Teams**: `filter_team(request)` and `filter_team_post(request)`  
- **View Team Details**: `team_details(request)`  
- **Compare Teams**: `compare_teams(request)` and `compare_teams_post(request)`  

---

## Database Models

### Drivers Collection
| Field | Description |
|-------|-------------|
| name | Driver's name |
| age | Driver's age |
| total_pole_positions | Total pole positions |
| total_race_wins | Total race wins |
| total_points | Total championship points |
| total_world_titles | Total world titles |
| total_fastest_laps | Total fastest laps |
| team | Team ID the driver belongs to |

### Teams Collection
| Field | Description |
|-------|-------------|
| team_name | Name of the team |
| year_founded | Founding year of the team |
| total_pole_positions | Total pole positions |
| total_race_wins | Total races won |
| total_constructor_titles | Total constructor championships |
| finishing_position | Last season finishing position |

---

## Installation

1. Clone the repository:  
```bash
git clone https://github.com/shafancp/f1_formula.git
cd f1_formula
