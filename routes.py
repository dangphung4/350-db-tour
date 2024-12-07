from flask import render_template, request, redirect, url_for
from dbtour import dbtour_app
import sqlite3
import redis

redis_client = redis.Redis(db=9, decode_responses=True)

def get_db_connection():
    conn = sqlite3.connect('huge.db')
    conn.row_factory = sqlite3.Row
    return conn

@dbtour_app.route('/')
def index():
    conn = get_db_connection()
    
    # get params from url
    language_filter = request.args.get('language', 'All')
    type_filter = request.args.get('type', 'All')
    sort = request.args.get('sort', 'f.name')
    order = request.args.get('order', 'asc')
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    
    query = """
    SELECT f.id, f.name, f.type, f.latest_version, f.github_stars, p.name as language_name
    FROM FrameworksLibraries f
    JOIN ProgrammingLanguages p ON f.language_id = p.id
    """
    
    if language_filter != 'All':
        query += f" WHERE p.name = '{language_filter}'"
        if type_filter != 'All':
            query += f" AND f.type = '{type_filter}'"
    elif type_filter != 'All':
        query += f" WHERE f.type = '{type_filter}'"
    
    # sort columns
    if sort == 'name':
        sort_column = 'f.name'
    elif sort == 'type':
        sort_column = 'f.type'
    elif sort == 'language_name':
        sort_column = 'p.name'
    elif sort == 'latest_version':
        sort_column = 'f.latest_version'
    elif sort == 'github_stars':
        sort_column = 'f.github_stars'
    else:
        sort_column = 'f.name'  # default sort column
    
    query += f" ORDER BY {sort_column} {'DESC' if order == 'desc' else 'ASC'}"
    query += f" LIMIT {per_page} OFFSET {offset}"
    frameworks = conn.execute(query).fetchall()
    
    # count total rows
    count_query = "SELECT COUNT(*) as total FROM FrameworksLibraries f JOIN ProgrammingLanguages p ON f.language_id = p.id"
    if language_filter != 'All' or type_filter != 'All':
        count_query += " WHERE " + query.split("WHERE", 1)[1].split("ORDER BY", 1)[0]
    
    total = conn.execute(count_query).fetchone()['total']
    total_pages = (total - 1) // per_page + 1
    
    languages = conn.execute("SELECT DISTINCT name FROM ProgrammingLanguages").fetchall()
    types = conn.execute("SELECT DISTINCT type FROM FrameworksLibraries").fetchall()
    # get all framework names for the learning queue
    framework_names = conn.execute("SELECT name FROM FrameworksLibraries").fetchall()
    
    # get Redis data
    learning_queue = redis_client.lrange('tech:learning_queue', 0, -1)
    trending_tech = redis_client.zrevrange('tech:trending', 0, 4, withscores=True)
    
    conn.close()
    
    next_order = 'asc' if order == 'desc' else 'desc'
    
    return render_template('index.html', 
                         frameworks=frameworks, 
                         languages=languages, 
                         types=types,
                         framework_names=framework_names,
                         selected_language=language_filter, 
                         selected_type=type_filter,
                         page=page, 
                         total_pages=total_pages, 
                         sort=sort, 
                         order=next_order,
                         learning_queue=learning_queue,
                         trending_tech=trending_tech)

@dbtour_app.route('/add_to_queue', methods=['POST'])
def add_to_queue():
    technology = request.form.get('technology')
    if technology:
        redis_client.rpush('tech:learning_queue', technology)
    return redirect(url_for('index'))

@dbtour_app.route('/remove_from_queue', methods=['POST'])
def remove_from_queue():
    technology = request.form.get('technology')
    if technology:
        redis_client.lrem('tech:learning_queue', 1, technology)
    return redirect(url_for('index'))

@dbtour_app.route('/mark_trending', methods=['POST'])
def mark_trending():
    technology = request.form.get('technology')
    if technology:
        redis_client.zincrby('tech:trending', 1, technology)
    return redirect(url_for('index'))

@dbtour_app.route('/add_trending', methods=['POST'])
def add_trending():
    technology = request.form.get('technology')
    initial_score = request.form.get('score', 1, type=int)  # default score of 1 if not provided
    
    if technology:
        redis_client.zadd('tech:trending', {technology: initial_score})
    
    return redirect(url_for('index'))

@dbtour_app.route('/decrease_trending', methods=['POST'])
def decrease_trending():
    technology = request.form.get('technology')
    if technology:
        redis_client.zincrby('tech:trending', -1, technology)
        # remove if score drops to 0 or below
        score = redis_client.zscore('tech:trending', technology)
        if score <= 0:
            redis_client.zrem('tech:trending', technology)
    return redirect(url_for('index'))

@dbtour_app.route('/add', methods=['GET', 'POST'])
def add_data():
    if request.method == 'POST':
        conn = get_db_connection()
        
        name = request.form['name']
        language_id = request.form['language_id']
        type = request.form['type']
        first_release = request.form['first_release']
        latest_version = request.form['latest_version']
        github_stars = request.form['github_stars']
        
        conn.execute('INSERT INTO FrameworksLibraries (name, language_id, type, first_release, latest_version, github_stars) VALUES (?, ?, ?, ?, ?, ?)',
                     (name, language_id, type, first_release, latest_version, github_stars))
        conn.commit()
        conn.close()
        
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    languages = conn.execute('SELECT id, name FROM ProgrammingLanguages').fetchall()
    types = conn.execute('SELECT DISTINCT type FROM FrameworksLibraries').fetchall()
    conn.close()
    return render_template('add.html', languages=languages, types=types)

@dbtour_app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_framework(id):
    conn = get_db_connection()
    
    if request.method == 'POST':
        name = request.form['name']
        language_id = request.form['language_id']
        type = request.form['type']
        first_release = request.form['first_release']
        latest_version = request.form['latest_version']
        github_stars = request.form['github_stars']
        
        ## update the framework using params from the form
        conn.execute('UPDATE FrameworksLibraries SET name = ?, language_id = ?, type = ?, first_release = ?, latest_version = ?, github_stars = ? WHERE id = ?',
                     (name, language_id, type, first_release, latest_version, github_stars, id))
        conn.commit()
        return redirect(url_for('index'))
    
    ## get the framework to edit and get languages for dropdown
    framework = conn.execute('SELECT * FROM FrameworksLibraries WHERE id = ?', (id,)).fetchone()
    languages = conn.execute('SELECT * FROM ProgrammingLanguages').fetchall()
    types = conn.execute('SELECT DISTINCT type FROM FrameworksLibraries').fetchall()
    
    conn.close()
    
    return render_template('edit.html', framework=framework, languages=languages, types=types)

