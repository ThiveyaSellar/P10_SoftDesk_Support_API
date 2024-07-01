# P10_SoftDesk_Support

## About this project

SoftDesk, a publisher of collaboration software, has decided to release an application for reporting and tracking technical problems.

## Installation


- Clone remote repository :

```
git clone https://github.com/ThiveyaSellar/P10_SoftDesk_Support_API.git
```

- Create a virtual environment in the project :
```
python -m venv env
```

- Activate virtual environment :
- Linux :
```
source env/bin/activate
```
- Windows :
```
env\Scripts\activate.bat
```

- Install the necessary packages from requirements.txt :
```
pip install -r requirements.txt
```
- Go to the softdesk_support directory and launch the local server :
```
python manage.py runserver
```

## Administration

To access Django's administration interface, you need to be a superuser.

- Create a superuser :
```
python manage.py createsuperuser
```
- Start the local server :
```
python manage.py runserver
```
- Go to http://127.0.0.1:8000/admin and log in if you are a superuser.

# Flake8

Flake8 is a package for checking that code complies with PEP8 guidelines.
- Configuration file : tox.ini
- Generate flake 8 report :
```
flake8
```

# API

- Ressources :
    - User
      - Create an user account : POST /sign-up
      - Login : POST /login
      - Create a user : POST /users/
      - Get a user : GET /users/{user_id}/
      - Update a user : PATCH /users/{user_id}/
      - Delete a user : DELETE /users/{user_id}/
      - Get all users : GET /users/ 
    - Project
      - POST /projects/ 
      - GET /projects/{project_id}/ 
      - PATCH /projects/{project_id}/ 
      - DELETE /projects/{project_id}/ 
      - GET /users/{user_id}/ 
      - POST /projects/{project_id}/add_contributor
      - POST /projects/{project_id}/delete_contributor
    - Issue
      - POST /projects/{project_id}/tickets/ 
      - GET /projects/{project_id}/tickets/{ticket_id}/ 
      - PATCH /projects/{project_id}/tickets/{ticket_id}/change_status 
      - PATCH /projects/{project_id}/tickets/{ticket_id}/ 
      - PATCH /projects/{project_id}/tickets/{ticket_id}/assign_contributor 
      - DELETE /projects/{project_id}/tickets/{ticket_id}/ 
      - GET /projects/{project_id}/tickets/ 
      - GET /users/{user_id}/projects/{project_id}/tickets/
    - Comment
      - POST /issues/{issue_id}/comments/ 
      - GET /issues/{issue_id}/comments/{comment_id}/ 
      - PATCH /issues/{issue_id}/comments/{comment_id}/ 
      - DELETE /issues/{issue_id}/comments/{comment_id}/ 
      - GET /issues/{issue_id}/comments/

