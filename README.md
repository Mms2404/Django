# DJANGO for Plant Shop and Expense Tracker 

Hi there , here lies the backend for the Plant Shop and Expense Tracker of my APP REPO .

## Get an idea to start with Django from here :

### 1. Set Up Ur Environment :
 - **Create a new folder** for your project.
 - In ur project directory :
 - ``` bash
    -  pip install pipenv
    -  pipenv shell
    -  pipenv install Django
    -  pip freeze  [ to see all the packages installed in ur environment ]

### 2.Create Ur Django Project :
 - ```bash
    - django-admin startproject <projectName>  # e.g., Expense_Tracker
    - Look inside my files . I’ve added comments in the code to help.
    - ls      [ this lists the components of ur projects ]

### 3.Create Ur App :
 - ```bash
    - python manage.py startapp <app name>  # e.g., Expense_Tracker_app
    - python manage.py runserver    - runs the server 
 - In <appname>/app.py, define your app name and class.
 - In <projectName>/settings.py, add your app to the INSTALLED_APPS list.
 - In the project-level urls.py, add the path to your app’s URL file (create this url.py file).
 - Look at the views.py

### Handle migrations :
 - After setting up your models in models.py :
    ``` bash
      - python manage.py makemigrations
      - python manage.py migrate
 - To interact with the database :
    ``` bash
      - python manage.py shell

### Connect Flutter and Django :
 - pip install djangorestframework
 - Add "rest_framework" to INSTALLED_APPS in "settings.py"
 - Create serializers ( look at the serializers file )

### Use THE WONDERFUL Django admin :
 - Create a superuser
    ```bash
      python manage.py createsuperuser
 - Follow the prompts for username, email, and password.
 - Now run the server and go to http://127.0.0.1:8000/admin and look at the admin panel you created in just two lines of 
   code .

### Add static assets to ur app :
 - Create a static folder for styles, images, etc., to improve performance.
 - In setting.py , add :
    STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),  # Don't forget that comma!
    )

#### I didnt dive deep into Django forms ,Flutter + Firebase is enough for my needs!
 
