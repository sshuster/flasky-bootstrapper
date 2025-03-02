
# SpeedWager - Car Racing Betting Platform

A responsive web application built with Flask and Bootstrap for placing bets on car races.

## Features

- User authentication system (register, login, logout)
- Virtual balance system for placing bets
- Browse upcoming, live, and completed races
- Place bets on drivers with different odds
- Track betting history and results
- Responsive design with Bootstrap 5
- Custom CSS styling and animations

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

```
python app.py
```

The application will be available at http://127.0.0.1:5000/

## Project Structure

- `app.py` - Main Flask application with routes and database models
- `templates/` - HTML templates using Jinja2
- `static/` - Static files (CSS, JavaScript, images)

## Database

The application uses SQLite with SQLAlchemy ORM and includes the following models:
- User - For authentication and storing user balance
- Race - Information about races
- Driver - Drivers participating in races with their odds
- Bet - Stores user bets and their status

## Demo Account

When you first run the application, you'll need to register an account. Each new user automatically receives $100 in virtual currency for placing bets.
