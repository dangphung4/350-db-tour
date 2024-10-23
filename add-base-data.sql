-- SQLite
-- Programming Languages Table
CREATE TABLE ProgrammingLanguages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    first_appeared INTEGER,
    latest_version TEXT,
    is_compiled BOOLEAN
);

-- Frameworks and Libraries Table
CREATE TABLE FrameworksLibraries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    language_id INTEGER,
    type TEXT NOT NULL,
    first_release INTEGER,
    latest_version TEXT,
    github_stars INTEGER,
    FOREIGN KEY (language_id) REFERENCES ProgrammingLanguages(id)
);

-- Sample data for ProgrammingLanguages
INSERT INTO ProgrammingLanguages (name, type, first_appeared, latest_version, is_compiled) VALUES
('JavaScript', 'Scripting', 1995, 'ES2023', 0),
('C#', 'Object-Oriented', 2000, '11.0', 1),
('Python', 'Multi-paradigm', 1991, '3.11.4', 0),
('Java', 'Object-Oriented', 1995, '20', 1),
('TypeScript', 'Typed Superset of JavaScript', 2012, '5.1', 0),
('Rust', 'Multi-paradigm', 2010, '1.70.0', 1),
('Go', 'Concurrent', 2009, '1.20', 1),
('Swift', 'Multi-paradigm', 2014, '5.8', 1),
('Kotlin', 'Multi-paradigm', 2011, '1.8.21', 1),
('Ruby', 'Multi-paradigm', 1995, '3.2.2', 0);

-- Sample data for FrameworksLibraries
INSERT INTO FrameworksLibraries (name, language_id, type, first_release, latest_version, github_stars) VALUES
('React', 1, 'Frontend Framework', 2013, '18.2.0', 203000),
('.NET', 2, 'Application Framework', 2002, '7.0', 18000),
('Django', 3, 'Web Framework', 2005, '4.2', 68000),
('Spring', 4, 'Application Framework', 2002, '6.0.9', 68000),
('Angular', 5, 'Frontend Framework', 2010, '16.0.0', 87000),
('Vue.js', 1, 'Frontend Framework', 2014, '3.3.4', 203000),
('Express.js', 1, 'Web Application Framework', 2010, '4.18.2', 60000),
('ASP.NET Core', 2, 'Web Application Framework', 2016, '7.0', 30000),
('React Native', 1, 'Mobile Application Framework', 2015, '0.71.8', 108000),
('Flutter', 8, 'Mobile Application Framework', 2017, '3.10.0', 152000),
('Ruby on Rails', 10, 'Web Application Framework', 2004, '7.0.5', 52000),
('Laravel', 3, 'Web Application Framework', 2011, '10.x', 73000),
('TensorFlow', 3, 'Machine Learning Library', 2015, '2.12.0', 172000),
('Pandas', 3, 'Data Analysis Library', 2008, '2.0.2', 37000),
('Node.js', 1, 'Runtime Environment', 2009, '20.2.0', 93000),
('Xamarin', 2, 'Mobile Application Framework', 2011, '5.0', 8000),
('Blazor', 2, 'Web Framework', 2018, '7.0', 11000),
('Next.js', 1, 'React Framework', 2016, '13.4.4', 106000),
('FastAPI', 3, 'Web Framework', 2018, '0.97.0', 59000),
('Svelte', 1, 'Frontend Framework', 2016, '3.59.1', 67000);