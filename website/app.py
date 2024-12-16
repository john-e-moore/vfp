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
    
    # Assume "position" is the column we want to filter on
    if 'position' in df.columns:
        # Extract unique positions
        positions = sorted(df['position'].dropna().unique().tolist())
    else:
        positions = []

    # Apply filter if provided
    filter_value = request.args.get('filter')
    if filter_value and filter_value.lower() != 'all':
        data = [row for row in data if str(row.get('position', '')).lower() == filter_value.lower()]

    return render_template('home.html', columns=columns, data=data, positions=positions)

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/download_csv')
def download_csv():
    return send_file(DATA_PATH, as_attachment=True, download_name='data.csv')

if __name__ == '__main__':
    app.run(debug=True)
