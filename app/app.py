from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from datetime import datetime
import random

#-------- Create the databases --------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'softwareengieeringboyz'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'signin'
mail = Mail(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    phonenum = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    userType = db.Column(db.String(80), nullable=False)
    def get_id(self):
        return str(self.id)

class Lotto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    pricePerTicket = db.Column(db.Float(), nullable=False)
    startDate = db.Column(db.Date, nullable=False)
    endDate = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(500), nullable=False)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lotto_id = db.Column(db.Integer, db.ForeignKey('lotto.id'), nullable=False)
    ticket_number1 = db.Column(db.Integer, nullable=False)
    ticket_number2 = db.Column(db.Integer, nullable=False)
    ticket_number3 = db.Column(db.Integer, nullable=False)
    ticket_number4 = db.Column(db.Integer, nullable=False)
    ticket_number5 = db.Column(db.Integer, nullable=False)
    card_number = db.Column(db.String(16), nullable=False)
    expiration_date = db.Column(db.String(5), nullable=False)
    billing_address = db.Column(db.String(255), nullable=False)

    user = db.relationship('User', backref='tickets')
    lotto = db.relationship('Lotto', backref='tickets')

class Winner(db.Model):
    key_id = db.Column(db.Integer, primary_key=True)
    lotto_id = db.Column(db.Integer, nullable=False)
    ticket_number1 = db.Column(db.Integer, nullable=False)
    ticket_number2 = db.Column(db.Integer, nullable=False)
    ticket_number3 = db.Column(db.Integer, nullable=False)
    ticket_number4 = db.Column(db.Integer, nullable=False)
    ticket_number5 = db.Column(db.Integer, nullable=False)


#-------- Routing --------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if request.method == 'POST':
        return redirect(url_for('signin'))
    return render_template('index.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            
            login_user(user)
            flash('Login successful!', 'success')
            if user.userType == "user":
                return redirect(url_for('user_dashboard'))
            elif user.userType == "admin":
                return redirect(url_for('admin_dashboard'))
            else:
                return render_template('error.html')
        else:
            flash('Login failed. Please check your credentials.', 'danger')

    return render_template('signin.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# Create login info
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        birthday_str = request.form['birthday']
        birthday = datetime.strptime(birthday_str, '%Y-%m-%d').date() if birthday_str else None # Converts date to correct format
        phonenum = request.form['phonenum']
        email = request.form['email']

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('error.html', message='Username already exists. Please choose another.')
        
        # Check if phone number is correct length
        if not (10 <= len(phonenum) <= 15):
            return render_template('error.html', message='Please enter a valid phone number (10-15 digits).')
        
        # Check if as @ (assume @ means valid email)
        if '@' not in email:
            return render_template('error.html', message='Please enter a valid email address.')

        if birthday:
            today = datetime.now().date()
            age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
            if age < 18:
                return render_template('error.html', message='You must be at least 18 years old to register.')
        # Create a new user
        new_user = User(username=username, password=password, birthday=birthday, phonenum=phonenum, email=email, userType="user")
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/admin_creation', methods=['GET', 'POST'])
def admin_creation():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        #Convert the birthday from html input format to python datetime format
        birthday_str = request.form['birthday']
        birthday = datetime.strptime(birthday_str, '%Y-%m-%d').date() if birthday_str else None
        phonenum = request.form['phonenum']
        email = request.form['email']

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('error.html', message='Username already exists. Please choose another.')
        
        # Check if phone number is correct length
        if not (10 <= len(phonenum) <= 15):
            return render_template('error.html', message='Please enter a valid phone number (10-15 digits).')
        
        # Check if as @ (assume @ means valid email)
        if '@' not in email:
            return render_template('error.html', message='Please enter a valid email address.')

        # Create a new admin
        new_user = User(username=username, password=password, birthday=birthday, phonenum=phonenum, email=email, userType="admin")
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('index'))
    return render_template('admin_creation.html')

# Remove users/login info 
@app.route('/remove_user', methods=['POST'])
def remove_user():
    if request.method == 'POST':
        user_id = request.form['user_id']
        user = User.query.get(user_id)

        if user:
            db.session.delete(user)
            db.session.commit()

    return redirect(url_for('user_list'))

# Remove lotto info 
@app.route('/remove_lotto', methods=['POST'])
def remove_lotto():
    if request.method == 'POST':
        lotto_id = request.form['lotto_id']
        lotto = Lotto.query.get(lotto_id)

        if lotto:
            db.session.delete(lotto)
            db.session.commit()

    return redirect(url_for('user_lotto_list'))

# add a new lottery
@app.route('/add_lotto', methods=['GET', 'POST'])
def add_lotto():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price_per_ticket = float(request.form['pricePerTicket'])
        start_date_str = request.form['startDate']
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()if start_date_str else None
        end_date_str = request.form['endDate']
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()if end_date_str else None

        new_lotto = Lotto(name=name, description=description, pricePerTicket=price_per_ticket, startDate=start_date, endDate=end_date)
        db.session.add(new_lotto)
        db.session.commit()

        return redirect(url_for('admin_dashboard'))

    return render_template('add_lotto.html')

# View user database
@app.route('/user_list')
def user_list():
    users = User.query.all()
    return render_template('user_list.html', users=users)

# view lotto database
@app.route('/user_lotto_list')
def user_lotto_list():
    lottos = Lotto.query.all()
    totals = ticket_counter()
    return render_template('user_lotto_list.html', lottos=lottos, totals=totals)

# View ticket database
@app.route('/tickets_sold')
def tickets_sold():
    tickets = Ticket.query.join(User).join(Lotto).all()
    return render_template('tickets_sold.html', tickets=tickets)

# Create dashboards
@app.route('/user_dashboard')
def user_dashboard():
    lottos = Lotto.query.all()
    return render_template('user_dashboard.html', current_user=current_user, lottos=lottos)

@app.route('/admin_dashboard')
def admin_dashboard():
    lottos = Lotto.query.all()
    return render_template('admin_dashboard.html', current_user=current_user, lottos=lottos)

# Create customer profile
@app.route('/customer_profile', methods=['GET'])
def customer_profile():
    username = current_user.username  # Assuming current_user has a 'username' attribute
    user = User.query.filter_by(username=username).first()

    if user:
        return render_template('customer_profile.html', user=user)

    return render_template('error.html', message='User not found')

# Create Order History
@app.route('/order_history', methods=['GET'])
def order_history():
    user_id= current_user.id
    tickets = Ticket.query.filter_by(user_id=user_id).all()
    return render_template('order_history.html', tickets=tickets)

# create search results 
@app.route('/search', methods=['GET'])
def search():
    search_query = request.args.get('q', '').strip()

    if not search_query:
        return redirect(url_for('user_dashboard'))

    # Perform the search in the Lotto model based on name or description
    results = Lotto.query.filter(
        (Lotto.name.ilike(f"%{search_query}%")) |
        (Lotto.description.ilike(f"%{search_query}%"))
    ).all()

    return render_template('search_results.html', results=results, search_query=search_query)

# Create purchase page
@app.route('/purchase/<int:lotto_id>', methods=['GET', 'POST'])
def purchase(lotto_id):

    lotto = Lotto.query.get_or_404(lotto_id)
    user_id = current_user.id

    # Check if the user has already purchased 10 tickets for this lotto
    ticket_count_for_lotto = Ticket.query.filter_by(user_id=user_id).count()

    # If the user has 4 tickets, dont allow them to buy any
    if ticket_count_for_lotto >= 10:
        flash('You have already purchased the maximum allowed tickets for this lotto.', 'warning')
        return redirect(url_for('user_dashboard'))

    if request.method == 'POST':
 

        # Retrieve additional information from the form
        ticket_number1 = request.form.get('ticket_number1')
        ticket_number2 = request.form.get('ticket_number2')
        ticket_number3 = request.form.get('ticket_number3')
        ticket_number4 = request.form.get('ticket_number4')
        ticket_number5 = request.form.get('ticket_number5')
        card_number = request.form.get('card_number')
        expiration_date = request.form.get('expiration_date')
        billing_address = request.form.get('billing_address')

        # Create a new ticket with card information
        new_ticket = Ticket(
            user_id=user_id,
            lotto_id=lotto_id,
            ticket_number1 = ticket_number1,
            ticket_number2 = ticket_number2,
            ticket_number3 = ticket_number3,
            ticket_number4 = ticket_number4,
            ticket_number5 = ticket_number5,
            card_number=card_number,
            expiration_date=expiration_date,
            billing_address=billing_address
        )
        db.session.add(new_ticket)
        db.session.commit()

        flash('Ticket purchased successfully!', 'success')
        return redirect(url_for('user_dashboard'))  # Redirect to the dashboard or another page

    return render_template('purchase.html', lotto=lotto)


# Create purchase page
@app.route('/add_winner/<int:lotto_id>', methods=['GET', 'POST'])
def add_winner(lotto_id):
    lotto = Lotto.query.get_or_404(lotto_id)

    if request.method == 'POST':
        # Retrieve additional information from the form
        ticket_number1 = request.form.get('ticket_number1')
        ticket_number2 = request.form.get('ticket_number2')
        ticket_number3 = request.form.get('ticket_number3')
        ticket_number4 = request.form.get('ticket_number4')
        ticket_number5 = request.form.get('ticket_number5')

        # Validate that ticket numbers are provided
        if None in [ticket_number1, ticket_number2, ticket_number3, ticket_number4, ticket_number5]:
            flash('Please provide all ticket numbers.', 'danger')
            return redirect(url_for('add_winner', lotto_id=lotto_id))

        # Create a new winner with valid ticket information
        new_winner = Winner(
            lotto_id=lotto_id,
            ticket_number1=ticket_number1,
            ticket_number2=ticket_number2,
            ticket_number3=ticket_number3,
            ticket_number4=ticket_number4,
            ticket_number5=ticket_number5,
        )
        db.session.add(new_winner)
        db.session.commit()

        flash('Winner added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))  # Redirect to the dashboard or another page

    # Generate random numbers for initial form display
    random_numbers = random.sample(range(1, 51), 5)
    return render_template('add_winner.html', lotto=lotto, random_numbers=random_numbers)
   

@app.route('/ticket_counter')
def ticket_counter():
    subquery = (db.session.query(Ticket.lotto_id, func.count(Ticket.id).label('ticket_count')).group_by(Ticket.lotto_id).subquery())
    ticket_costs = (db.session.query(subquery.c.lotto_id, func.sum(Lotto.pricePerTicket * subquery.c.ticket_count).label('total_cost')).join(Lotto, subquery.c.lotto_id == Lotto.id).group_by(subquery.c.lotto_id).all())
    return render_template('ticket_counter.html', ticket_costs=ticket_costs)

@app.route('/view_winners')
def view_winners():
    winners = Winner.query.all()
    return render_template('view_winners.html', winners=winners)

@app.route('/check_winner', methods=['GET', 'POST'])
@login_required  # Make sure the user is logged in to access this page
def check_winner():
    if request.method == 'POST':
        user_id = current_user.id
        lotto_id = request.form.get('lotto_id')  # Use lotto_id instead of id

        # Fetch the most recent winning ticket for the specified lotto
        recent_winner = Winner.query.filter_by(lotto_id=lotto_id).order_by(Winner.key_id.desc()).first()

        # Fetch the user's tickets for the specified lotto
        user_tickets = Ticket.query.filter_by(user_id=user_id, lotto_id=lotto_id).all()

        # Check if any of the user's tickets match the most recent winning ticket
        is_winner = any(
            ticket.ticket_number1 == recent_winner.ticket_number1 and
            ticket.ticket_number2 == recent_winner.ticket_number2 and
            ticket.ticket_number3 == recent_winner.ticket_number3 and
            ticket.ticket_number4 == recent_winner.ticket_number4 and
            ticket.ticket_number5 == recent_winner.ticket_number5
            for ticket in user_tickets
        )

        return render_template('check_winner.html', is_winner=is_winner, recent_winner=recent_winner)

    # Render the initial form to select a lotto
    lottos = Lotto.query.all()
    return render_template('check_winner.html', lottos=lottos)

#-------- Main --------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        #User.__table__.drop(db.engine) # Delete the database for development
        #Lotto.__table__.drop(db.engine) # Delete the database for development
        #Ticket.__table__.drop(db.engine) # Delete the database for development
        #Winner.__table__.drop(db.engine) # Delete the database for development

    app.run(debug=True)