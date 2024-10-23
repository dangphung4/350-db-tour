# Random Tech Stuff Database Tour

This project is a Flask-based web application that showcases various programming languages, frameworks, and libraries. It allows users to browse through a curated list of technologies, filter them by language and type, and even add new entries to the database.

## Features

- Browse a list of programming languages, frameworks, and libraries
- Filter entries by programming language and type
- Pagination for easy navigation through large datasets
- Add new frameworks or libraries to the database

## Technologies Used

- Python 3.x
- Flask
- SQLite
- HTML/CSS (with Tailwind CSS for styling)

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/random-tech-stuff.git
   cd random-tech-stuff
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```
   sqlite3 huge.db < add-base-data.sql
   ```

5. Run the application:
   ```
   python dbtour_app.py
   ```

6. Open your web browser and navigate to `http://localhost:5000` to view the application.

## Project Structure

- `dbtour_app.py`: The main entry point of the application
- `dbtour/__init__.py`: Initializes the Flask application
- `dbtour/routes.py`: Contains all the route definitions and main logic
- `templates/`: Contains all the HTML templates
  - `base.html`: The base template that other templates extend
  - `index.html`: The main page showing the list of frameworks and libraries
  - `add.html`: The form for adding new entries
- `add-base-data.sql`: SQL script to initialize the database with sample data
