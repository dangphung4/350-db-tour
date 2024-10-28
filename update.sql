UPDATE FrameworksLibraries
SET 
    latest_version = CASE 
        WHEN name = 'React' THEN '18.2.0'
        WHEN name = '.NET' THEN '8.0'
        WHEN name = 'Django' THEN '5.1.2'
        WHEN name = 'Spring' THEN '6.1.13'
        WHEN name = 'Angular' THEN '18.2.0'
        WHEN name = 'Vue.js' THEN '3.5.12'
        WHEN name = 'Express.js' THEN '4.19.2'
        WHEN name = 'ASP.NET Core' THEN '8.0.1'
        WHEN name = 'React Native' THEN '0.76.2'
        WHEN name = 'Flutter' THEN '3.16.0'
        WHEN name = 'Ruby on Rails' THEN '7.1.2'
        WHEN name = 'Laravel' THEN '11.1.0'
        WHEN name = 'TensorFlow' THEN '2.15.0'
        WHEN name = 'Pandas' THEN '2.1.3'
        WHEN name = 'Node.js' THEN '21.2.0'
        WHEN name = 'Xamarin' THEN '5.0.0.1'
        WHEN name = 'Blazor' THEN '8.0.0'
        WHEN name = 'Next.js' THEN '14.0.3'
        WHEN name = 'FastAPI' THEN '0.104.1'
        WHEN name = 'Svelte' THEN '4.2.3'
        ELSE latest_version
    END,
    github_stars = CASE 
        WHEN name = 'React' THEN 229000
        WHEN name = '.NET' THEN 28000
        WHEN name = 'Django' THEN 80000
        WHEN name = 'Spring' THEN 70000
        WHEN name = 'Angular' THEN 90000
        WHEN name = 'Vue.js' THEN 205000
        WHEN name = 'Express.js' THEN 62000
        WHEN name = 'ASP.NET Core' THEN 32000
        WHEN name = 'React Native' THEN 119000
        WHEN name = 'Flutter' THEN 157000
        WHEN name = 'Ruby on Rails' THEN 53000
        WHEN name = 'Laravel' THEN 75000
        WHEN name = 'TensorFlow' THEN 178000
        WHEN name = 'Pandas' THEN 39000
        WHEN name = 'Node.js' THEN 97000
        WHEN name = 'Xamarin' THEN 8000
        WHEN name = 'Blazor' THEN 13000
        WHEN name = 'Next.js' THEN 119000
        WHEN name = 'FastAPI' THEN 77000
        WHEN name = 'Svelte' THEN 79000
        ELSE github_stars
    END;