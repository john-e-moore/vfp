import os
from flask import Flask, render_template, send_file, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import glob
import datetime
import markdown

app = Flask(__name__)
app.secret_key = 'replace_with_a_random_secret_key'

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Flask-Login Setup
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

DATA_PATH = os.path.join(app.root_path, 'static', 'data', 'data.csv')

def get_blog_posts():
    blog_dir = os.path.join(app.root_path, 'static', 'blog_posts')
    posts = []
    for filepath in glob.glob(os.path.join(blog_dir, '*.md')):
        filename = os.path.basename(filepath)
        try:
            date_str = filename[:10]
            post_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        lines = content.split('\n')
        title_line = lines[0].strip()
        title = title_line.lstrip('#').strip()

        # Use only the content after the title line for the HTML conversion
        body_lines = lines[1:]
        html_content = markdown.markdown('\n'.join(body_lines))

        posts.append({
            'title': title,
            'date': post_date,
            'html_content': html_content
        })

    posts.sort(key=lambda x: x['date'], reverse=True)
    return posts

@app.route('/')
def home():
    # Show blog posts in reverse chronological order
    posts = get_blog_posts()
    return render_template('home.html', posts=posts)

@app.route('/projections')
@login_required
def projections():
    df = pd.read_csv(DATA_PATH)
    data = df.to_dict(orient='records')
    columns = df.columns.tolist()

    positions = sorted(df['position'].dropna().unique().tolist()) if 'position' in df.columns else []
    teams = sorted(df['team'].dropna().unique().tolist()) if 'team' in df.columns else []

    filter_position = request.args.get('filter_position', 'all')
    filter_team = request.args.get('filter_team', 'all')

    # Apply filters
    if filter_position.lower() != 'all':
        data = [row for row in data if str(row.get('position', '')).lower() == filter_position.lower()]
    if filter_team.lower() != 'all':
        data = [row for row in data if str(row.get('team', '')).lower() == filter_team.lower()]

    # Get last updated timestamp for data.csv
    last_updated_ts = os.path.getmtime(DATA_PATH)
    last_updated = datetime.datetime.fromtimestamp(last_updated_ts).strftime('%Y-%m-%d %H:%M:%S')

    return render_template('projections.html', 
                           columns=columns, 
                           data=data, 
                           positions=positions, 
                           teams=teams,
                           selected_position=filter_position,
                           selected_team=filter_team,
                           last_updated=last_updated)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/download_csv')
@login_required
def download_csv():
    return send_file(DATA_PATH, as_attachment=True, attachment_filename='data.csv')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Username already exists, please choose another one.')
            return redirect(url_for('signup'))
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Signup successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful.')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('projections'))
        else:
            flash('Invalid username or password.')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
