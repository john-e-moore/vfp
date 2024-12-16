from flask import Flask, render_template, send_file, request
import pandas as pd
import os

app = Flask(__name__)

DATA_PATH = os.path.join(app.root_path, 'static', 'data', 'data.csv')

@app.route('/')
def home():
    # Read the CSV data
    df = pd.read_csv(DATA_PATH)
    data = df.to_dict(orient='records')
    columns = df.columns.tolist()

    # Extract unique positions and teams if they exist
    positions = sorted(df['position'].dropna().unique().tolist()) if 'position' in df.columns else []
    teams = sorted(df['team'].dropna().unique().tolist()) if 'team' in df.columns else []

    # Get filter values from query parameters
    filter_position = request.args.get('filter_position', 'all')
    filter_team = request.args.get('filter_team', 'all')

    # Apply filters if set
    if filter_position.lower() != 'all':
        data = [row for row in data if str(row.get('position', '')).lower() == filter_position.lower()]
    if filter_team.lower() != 'all':
        data = [row for row in data if str(row.get('team', '')).lower() == filter_team.lower()]

    return render_template('home.html', 
                           columns=columns, 
                           data=data, 
                           positions=positions, 
                           teams=teams,
                           selected_position=filter_position,
                           selected_team=filter_team)

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/download_csv')
def download_csv():
    return send_file(DATA_PATH, as_attachment=True, download_name='data.csv')

if __name__ == '__main__':
    app.run(debug=True)
