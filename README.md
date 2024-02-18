# neofi-backend-api
Django REST framework, Docker, Gunicorn, SQLite, PostgreSQL, SwaggerDocs, Redocs

This project involves the development of a RESTful API for a note-taking application, allowing for basic CRUD operations on notes, including user authentication, note creation, sharing, updating, and accessing note version history.

### Basic Install
```bash
    #1 Clone the repository
    git clone https://github.com/yashahmad/neofi-backend-api.git
    
    #2 navigate to the project directory
    cd neofi-backend-api

    #3 Install dependencies
    pip install -r requirements.txt

    #4 Initialize the database
    python manage.py migrate

    #5 Run the server
    python manage.py runserver
```

### Dockerized Install
```bash
    #1 Clone the repository
    git clone https://github.com/yashahmad/neofi-backend-api.git
    
    #2 navigate to the project directory
    cd neofi-backend-api

    #3 to build docker local environment
    docker-compose -f docker-compose.yml up --build

    #4 Test url (Swagger Docs)
    http://localhost:8000/ 
```

```bash
    # Production
    #1 Clone the repository
    git clone https://github.com/yashahmad/neofi-backend-api.git
    
    #2 navigate to the project directory
    cd neofi-backend-api

    #3 run docker production file in detached mode
    docker-compose -f docker-compose.prod.yml up -d

    #4 run migrations for the first time
    docker-compose -f docker-compose.prod.yml run web python manage.py migrate
```



### API Endpoints http://localhost:8000/v1/api
| Category            | Method | Endpoint                       | Description                               |
|---------------------|--------|--------------------------------|-------------------------------------------|
| User Authentication | POST   | `/signup`                      | Register a new user.                      |
| User Authentication | POST   | `/login`                       | Authenticate a user and return a token.   |
| Notes Management    | POST   | `/notes/create`                | Create a new note.                        |
| Notes Management    | GET    | `/notes/{id}`                  | Retrieve a specific note by its ID.       |
| Notes Management    | PUT    | `/notes/{id}`                  | Update an existing note.                  |
| Notes Management    | POST   | `/notes/share`                 | Share a note with other users.            |
| Version History     | GET    | `/notes/version-history/{id}`  | Retrieve all changes associated with a note. |
