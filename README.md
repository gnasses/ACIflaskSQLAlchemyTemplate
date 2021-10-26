# PythonFlaskSQLAlchemyTemplate
Contains a development framework and app skeleton for ACI WebApps and downstream APIs using Python/Flask/SQLAlchemy/Marshmallow. The repo is a fully working sample web application, a simple collection of ACI MAC Addresses to database, direct query of MAC address from ACI, and a query against the collected database. The purpose of this skeleton is to provide a base application that can be modified as needed for a new project. This ReadMe contains documentation as to how to clone this code, break the link to this repo, and create a new repo for the new application. These directions were tested using Windows, Anaconda, Git CLI. Exact command syntax may vary. Additional instructions are also provided below for basic Flask development app deployment as service on a RHEL development server. 

-----

## Cloning this repo
The first step to using the template is to make a local copy (clone) of the existing code
Be Sure to use the link to the main Repo (not master) and add .git to the end of the link. This will create a new directory with the same name as the starting Repo (PythonFlaskSQLAlchemyTemplate)

        git clone https://github.com/gnasses/PythonFlaskSQLAlchemyTemplate.git

Cloning a repo retains information about the origin, this must be removed to make your new project independent, and eventually live in its own repo. First go into your cloned directory

        cd PythonFlaskSQLAlchemyTemplate
        git remote remove origin

You can now change the name of the project folder to match your new project effort

-----

## Rehoming the application to a new Repo

#### Create the New Repo on GitHub
Go to github.
Log in to your account.
Click the new repository button in the top-right. **Be sure you do NOT check the button to create a new ReadMe file**

#### Link your Previously Cloned Code to your new GitHub Repo
Connect your local Repo to GitHub (Substitute the GitHub link below with the link to your new Repo) This assumes you have already entered the git config global commands to register your username and email. 

        git remote add origin https://github.com/user/NewRepoName 

Verify the local repo is linked to your new remote

        git remote -v

Sync local files up to GitHub

        git push -u origin master


-----

## Testing the existing application
Before getting into modifying the existing code to suit your purposes you should make sure it can run in it's existing form.

#### Move into the application directory and edit the util.py code to add your own **Read-Only** TACACS credentials in this section. 

        class CiscoDeviceRO:
            def __init__(self, host, username='your_tacacs_username', password='your_tacacs_password', device_type='cisco_ios', timeout=90, auth_timeout=90):

#### Install Python Pre-Requisites
In your python environment install the required libraries from Pypy

        pip install netmiko
        pip install flask
        pip install Flask-SQLAlchemy
        pip install flask-marshmallow
        pip install ntc-templates

#### Initialize the Database 
From the application directory launch a python window, import the DB function from the app, create table(s), then exit

        python
        >>> from app import db
        >>> db.create_all()
        >>> exit()
        
        
#### Launch the application 
From the application directory launch the application

        python app.py
        
or if Python3 is your default interpreter

        python app.py

You should now be able to view the app in your browser, pointed to the ip address where you ran it, using the default port of 5000
If you need to change the port the app runs on, edit the init line at the bottom of the app.py file. 

        app.run(host='127.0.0.1', port=5000)


-----

## Git Workflow Process for changes to your new application

1. Edit and make some changes to code
2. Add any changed/deleted files to be tracked by Git (or add all)
        
        git add . --all

3. Commit the changes to your local git

        git commit -m "commit notes"
        
4. Push changes to origin Repo

        git push

------

## Deploy to Linux: Making a Flask Application into a service using Systemd
This will allow the application to automatically start up after a system restart, and restart the application if it crashes or unloads for any reason. 

#### Create a Service Unit File

    cd /etc/systemd/system
    sudo vim <servicename>.service
 
#### Use the following as a template to define your service
Note: defining absolute paths are typically required. 

    [Unit]
    Description=Route Table Checkout Service
    After=network.target

    [Service]
    User=root
    WorkingDirectory=/var/www/html/Route_Validation_Flask_Prod
    ExecStart=/usr/bin/python3 /var/www/html/Route_Validation_Flask_Prod/route_diff.py
    Restart=always

    [Install]
    WantedBy=multi-user.target

#### Refresh Systemd configuration to see the new file

    sudo systemctl daemon-reload 
    
#### Start the application as a service
(Be sure the application is not already running!)

    sudo systemctl start <servicename>
    
#### Check the status of your service

    sudo systemctl status <servicename>
    
