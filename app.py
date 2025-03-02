
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///racing.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    balance = db.Column(db.Float, default=100.0)
    bets = db.relationship('Bet', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Race(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    race_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='upcoming')  # upcoming, live, completed
    winner_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=True)
    cars = db.relationship('Driver', backref='race', lazy=True)
    bets = db.relationship('Bet', backref='race', lazy=True)

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    car_model = db.Column(db.String(100), nullable=False)
    odds = db.Column(db.Float, nullable=False)
    race_id = db.Column(db.Integer, db.ForeignKey('race.id'), nullable=False)
    bets = db.relationship('Bet', backref='driver', lazy=True)

class Bet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    placed_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    race_id = db.Column(db.Integer, db.ForeignKey('race.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    status = db.Column(db.String(20), default='active')  # active, won, lost

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create sample data
def create_sample_data():
    # Check if we already have data
    if User.query.count() > 0:
        return
    
    # Create sample races
    race1 = Race(
        title="Monaco Grand Prix",
        description="The prestigious Monaco Grand Prix through the streets of Monte Carlo.",
        race_time=datetime.strptime("2023-12-10 14:00:00", "%Y-%m-%d %H:%M:%S"),
        status="upcoming"
    )
    
    race2 = Race(
        title="Indianapolis 500",
        description="The 107th running of the Indianapolis 500 at the Indianapolis Motor Speedway.",
        race_time=datetime.strptime("2023-12-15 15:30:00", "%Y-%m-%d %H:%M:%S"),
        status="upcoming"
    )
    
    db.session.add_all([race1, race2])
    db.session.commit()
    
    # Create drivers for races
    drivers = [
        Driver(name="Lewis Hamilton", car_model="Mercedes W12", odds=2.5, race_id=1),
        Driver(name="Max Verstappen", car_model="Red Bull RB16B", odds=2.2, race_id=1),
        Driver(name="Charles Leclerc", car_model="Ferrari SF21", odds=4.0, race_id=1),
        Driver(name="Scott Dixon", car_model="Dallara-Honda", odds=3.0, race_id=2),
        Driver(name="Josef Newgarden", car_model="Dallara-Chevrolet", odds=3.5, race_id=2),
        Driver(name="Helio Castroneves", car_model="Dallara-Honda", odds=5.0, race_id=2)
    ]
    
    db.session.add_all(drivers)
    db.session.commit()

# Routes
@app.route('/')
def index():
    upcoming_races = Race.query.filter_by(status='upcoming').order_by(Race.race_time).limit(3).all()
    return render_template('index.html', title='Home', races=upcoming_races)

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/contact')
def contact():
    return render_template('contact.html', title='Contact')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_exists = User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first()
        
        if user_exists:
            flash('Username or email already exists.')
            return redirect(url_for('register'))
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        
        flash('Invalid username or password')
    
    return render_template('login.html', title='Login')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/races')
def races():
    upcoming_races = Race.query.filter_by(status='upcoming').order_by(Race.race_time).all()
    live_races = Race.query.filter_by(status='live').all()
    completed_races = Race.query.filter_by(status='completed').order_by(Race.race_time.desc()).limit(5).all()
    return render_template('races.html', title='Races', 
                          upcoming_races=upcoming_races, 
                          live_races=live_races, 
                          completed_races=completed_races)

@app.route('/race/<int:race_id>')
def race_detail(race_id):
    race = Race.query.get_or_404(race_id)
    drivers = Driver.query.filter_by(race_id=race_id).all()
    return render_template('race_detail.html', title=race.title, race=race, drivers=drivers)

@app.route('/place_bet/<int:race_id>/<int:driver_id>', methods=['GET', 'POST'])
@login_required
def place_bet(race_id, driver_id):
    race = Race.query.get_or_404(race_id)
    driver = Driver.query.get_or_404(driver_id)
    
    if race.status != 'upcoming':
        flash('Betting is closed for this race.')
        return redirect(url_for('race_detail', race_id=race_id))
    
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        
        if amount <= 0:
            flash('Bet amount must be greater than zero.')
            return redirect(url_for('place_bet', race_id=race_id, driver_id=driver_id))
        
        if amount > current_user.balance:
            flash('Insufficient balance.')
            return redirect(url_for('place_bet', race_id=race_id, driver_id=driver_id))
        
        new_bet = Bet(
            amount=amount,
            user_id=current_user.id,
            race_id=race_id,
            driver_id=driver_id
        )
        
        current_user.balance -= amount
        
        db.session.add(new_bet)
        db.session.commit()
        
        flash(f'Your bet of ${amount:.2f} on {driver.name} has been placed!')
        return redirect(url_for('race_detail', race_id=race_id))
    
    return render_template('place_bet.html', title='Place Bet', race=race, driver=driver)

@app.route('/profile')
@login_required
def profile():
    active_bets = Bet.query.filter_by(user_id=current_user.id, status='active').all()
    bet_history = Bet.query.filter(Bet.user_id==current_user.id, Bet.status!='active').order_by(Bet.placed_at.desc()).all()
    return render_template('profile.html', title='My Profile', 
                          active_bets=active_bets, 
                          bet_history=bet_history)

# Initialize database before first request
@app.before_first_request
def before_first_request():
    db.create_all()
    create_sample_data()

if __name__ == '__main__':
    app.run(debug=True)
