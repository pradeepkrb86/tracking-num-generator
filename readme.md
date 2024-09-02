
# Tracking Number Generator

It implements a RESTful API that generates unique tracking numbers for parcels.
An instance of the project is deployed on AWS accessible at the below URL.
https://scalpro.online/next-tracking-number/


## Prerequisites

- Python 3.12.3
- Pip

> **Note:** The following components are only required when deploying the application in a production environment.

### Additional Requirements for Production
- **Gunicorn**: A Python WSGI HTTP server to serve the Django application.
- **Supervisor**: A process control system to manage and monitor Gunicorn.
- **Nginx**: A web server used as a reverse proxy to handle client requests.

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/my_project.git
cd my_project
```

### 2. Setup Virtual Environment(optional)
```bash
python3 -m venv venvname
source venvname/bin/activate
```

### 3. Install Dependencies
Use the package manager pip to install the dependencies.

```bash
  pip install requirements.txt
```
## Run Locally


Go to the project directory

```bash
  cd my-project
```

Start the server

```bash
  python manage.py runserver
```


## Deployment

### 1. Install gunicorn
```bash
pip install gunicorn
```

### 2. Setting up supervisor
#### 1. Install Supervisor
Run the following command to install Supervisor:

```bash
sudo apt-get install supervisor
```
#### 2. Create a supervisor configuration file for gunicorn
- Replace paths to my_project and venv with your project and virtualenvs.
- Replace your_user with the username that will run the process.

```bash
[program:my_project]
command=/path/to/venv/bin/gunicorn --workers 3 my_project.wsgi:application
directory=/path/to/my_project
user=your_user
autostart=true
autorestart=true
stderr_logfile=/var/log/my_project.err.log
stdout_logfile=/var/log/my_project.out.log
```
#### 3. Reload Supervisor and start gunicorn


```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start my_project
```
### 3. Setting up Nginx
#### 1. Install Nginx
Run the following command to install Nginx:

```bash
sudo apt-get install nginx
```
#### 2. Create a configuration file for your project.
- Create a configuration file named your_project.conf inside the /etc/nginx/sites-available/ directory.
- Create a symlink inside the /etc/nginx/sites-enabled/ to the your_project.conf configuration file in /etc/nginx/sites-available/ directory.


#### 3. Edit your_project.conf inside /etc/nginx/sites-available/ directory.


```bash
server{
        server_name your_domain.extension www.your_domain.extension;
        location /next-tracking-number/ {
                include proxy_params;
                proxy_pass http://path/to/your_django_project/app.sock;

        }     

}

```

### 4. Setting up HTTPS for the app using Certbot
#### 1.  Install Certbot and the Nginx Plugin
Run the following commands

```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx
```

#### 2.  Obtain an SSL Certificate
Run the following commands

```bash
sudo certbot --nginx -d your_domain.extension -d www.your_domain.extension
```

#### 3.  Update your_project.conf if not automatically upated and it needs to be like below.

```bash
server{
        server_name your_domain.extension www.your_domain.extension;

        location /next-tracking-number/ {
                include proxy_params;
                proxy_pass http://unix:/home/ubuntu/generator/app.sock;

        }   
    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/scalpro.online/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/scalpro.online/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

}
server{
    if ($host = www.your_domain.extension) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    if ($host = your_domain.extension) {
        return 301 https://$host$request_uri;
    } # managed by Certbot
        listen 80;
        server_name your_domain.extension www.your_domain.extension;
    return 404; # managed by Certbot
}
```

## Running Tests

To run tests, run the following command

```bash
  python manage.py test trackingnum.test_suite --verbosity=2
```

> **Note:** Please update the url for production as per your domain in the tests.py file and test environment(to localhost).

## Additional Notes

- **Concurrency Handling**: In production the application uses `gevent` workers in Gunicorn, allowing it to handle multiple requests concurrently within each worker.

- **Error Handling**: The application includes basic error handling, but logging should be monitored to catch any unhandled exceptions during runtime.
- 
- **Scalability**: Different instances of the application have access to the tracking number data from shared database which allows for horizonal scalability.For increased load database can be changed to MySQL/PostgreSQL and create different server instances if required.

- **Deployment**: The project is currently deployed using Gunicorn and Nginx on AWS.

