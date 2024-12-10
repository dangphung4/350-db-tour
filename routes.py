from flask import render_template, request, redirect, url_for, flash
from dbtour import dbtour_app
import sqlite3
import redis
from pymongo import MongoClient
from bson import ObjectId
from neo4j import GraphDatabase


redis_client = redis.Redis(db=9,
                           password='BenAndJerrys',
                           decode_responses=True)
mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['dphung_db'] 
items_collection = mongo_db['items']  

db = mongo_client['dphung_db']
items = db['items']

# items.delete_many({})

# sample_items = [
#     {
#         "name": "React Hooks Introduction",
#         "technology": "React",
#         "version": "16.8",
#         "type": "Frontend",
#         "features": ["useState", "useEffect", "useContext"],
#         "complexity": "Medium",
#         "prerequisites": ["JavaScript", "React Basics"]
#     },
#     {
#         "name": "Django REST Framework",
#         "technology": "Django",
#         "version": "3.12",
#         "type": "Backend",
#         "features": ["Serializers", "ViewSets", "Authentication"],
#         "use_cases": ["API Development", "Web Services"]
#     }
# ]

# items.insert_many(sample_items)

def get_db_connection():
    conn = sqlite3.connect('huge.db')
    conn.row_factory = sqlite3.Row
    return conn

neo4j_uri = "bolt://localhost:7687"
neo4j_driver = GraphDatabase.driver(
    neo4j_uri,
    auth=("neo4j", "BenAndJerrys"),
    database="neo4j"
)

def get_neo4j_session():
    return neo4j_driver.session()

def init_neo4j():
    with get_neo4j_session() as session:
        session.run("""
            CREATE CONSTRAINT technology_mongo_id IF NOT EXISTS
            FOR (t:Technology) REQUIRE t.mongo_id IS UNIQUE
        """)

init_neo4j()


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

@dbtour_app.route('/items')
def list_items():
    filter_key = request.args.get('key')
    filter_value = request.args.get('value')
    
    query = {}
    if filter_key and filter_value:
        query[filter_key] = filter_value
    
    items = list(items_collection.find(query))
    
    with get_neo4j_session() as session:
        for item in items:
            query = """
                MATCH (source:Technology {mongo_id: $item_id})-[r]->(target:Technology)
                RETURN type(r) as type, elementId(r) as id, 
                       target.name as target_name, target.mongo_id as target_id
            """
            result = session.run(query, item_id=str(item['_id']))
            
            item['relationships'] = [
                {
                    'id': record['id'],
                    'type': record['type'].lower(),
                    'target_name': record['target_name'],
                    'target_id': record['target_id']
                }
                for record in result
            ]
    
    return render_template('items.html', 
                         items=items,
                         filter_key=filter_key,
                         filter_value=filter_value)

@dbtour_app.route('/item/<item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    if request.method == 'POST':
        if 'new_key' in request.form and 'new_value' in request.form:
            new_key = request.form['new_key']
            new_value = request.form['new_value']
            if new_key and new_value:
                items_collection.update_one(
                    {'_id': ObjectId(item_id)},
                    {'$set': {new_key: new_value}}
                )
        else:
            update_data = {k: v for k, v in request.form.items() if k != '_id'}
            items_collection.update_one(
                {'_id': ObjectId(item_id)},
                {'$set': update_data}
            )
        return redirect(url_for('list_items'))
    
    # GET request - show edit form
    item = items_collection.find_one({'_id': ObjectId(item_id)})
    return render_template('edit_item.html', item=item)


@dbtour_app.route('/reset_items', methods=['POST'])
def reset_items():
    """Reset the items collection to the initial sample data."""
    try:
        sample_items = [
            {
                "name": "React Hooks Introduction",
                "technology": "React",
                "version": "16.8",
                "type": "Frontend",
                "features": ["useState", "useEffect", "useContext"],
                "complexity": "Medium",
                "prerequisites": ["JavaScript", "React Basics"]
            },
            {
                "name": "Django REST Framework",
                "technology": "Django",
                "version": "3.12",
                "type": "Backend",
                "features": ["Serializers", "ViewSets", "Authentication"],
                "use_cases": ["API Development", "Web Services"]
            },
            {
                "name": "Flask Tutorial",
                "technology": "Flask",
                "version": "2.3",
                "type": "Backend",
                "features": ["Routing", "Templates", "Database Integration"],
                "complexity": "Beginner"
            }
        ]
        
        items_collection.delete_many({})
        items_collection.insert_many(sample_items)
        return redirect(url_for('list_items'))
    except Exception as e:
        return redirect(url_for('list_items'))

@dbtour_app.route('/add_item', methods=['POST'])
def add_item():
    name = request.form['name']
    if name:
        new_item = {
            "name": name,
            "technology": "Not specified",
            "type": "Not specified"
        }
        items_collection.insert_one(new_item)
    return redirect(url_for('list_items'))

@dbtour_app.route('/add_relationship/<item_id>', methods=['POST'])
def add_relationship(item_id):
    relationship_type = request.form.get('relationship_type')
    target_id = request.form.get('target_id')
    
    if not relationship_type or not target_id:
        return redirect(url_for('list_items'))
    
    source_item = items_collection.find_one({'_id': ObjectId(item_id)})
    target_item = items_collection.find_one({'_id': ObjectId(target_id)})
    
    if not source_item or not target_item:
        return redirect(url_for('list_items'))
    
    with get_neo4j_session() as session:
        query = """
            MERGE (source:Technology {mongo_id: $source_id})
            SET source.name = $source_name
            MERGE (target:Technology {mongo_id: $target_id})
            SET target.name = $target_name
            WITH source, target
            CREATE (source)-[r:`$rel_type`]->(target)
            RETURN source, target, r
        """
        
        try:
            session.run(
                query,
                source_id=str(source_item['_id']),
                source_name=source_item['name'],
                target_id=str(target_item['_id']),
                target_name=target_item['name'],
                rel_type=relationship_type.upper()
            )
        except Exception as e:
            pass
    
    return redirect(url_for('list_items'))

@dbtour_app.route('/remove_relationship/<item_id>', methods=['POST'])
def remove_relationship(item_id):
    relationship_id = request.form.get('relationship_id')
    
    with get_neo4j_session() as session:
        query = """
            MATCH (source:Technology)-[r]->(target:Technology)
            WHERE elementId(r) = $rel_id
            DELETE r
        """
        try:
            session.run(query, rel_id=relationship_id)
        except Exception as e:
            pass
    
    return redirect(url_for('list_items'))

