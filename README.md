# Python Flask Login Example
This is a flask api example login project which supports multi factor authentication using one time pad's.


## Environment Variables
| Key                   | Description                                | Default              |
|-----------------------|--------------------------------------------|----------------------|
| MYSQL_USERNAME        |                                            | root                 |
| MYSQL_PASSWORD        |                                            |                      |
| MYSQL_HOSTNAME        |                                            | mariadb              |
| MYSQL_PORT            |                                            | 3306                 |
| MYSQL_DATABASE        |                                            | example              |
| REDIS_HOSTNAME        |                                            | redis                |
| REDIS_PORT            |                                            | 6379                 |
| REDIS_PASSWORD        |                                            |                      |
| REDIS_DATABASE        |                                            | 0                    |
|                       |                                            |                      ||

## Installation
1. [Install Docker](https://docs.docker.com/install/)

2. [Install docker-compose](https://docs.docker.com/compose/install/)
    ```bash
    sudo curl -L "https://github.com/docker/compose/releases/download/1.26.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ```

3. Build the docker image
   ```bash
   docker build -t pythonflasklogin:build -f Dockerfile.build .
   docker build -t pythonflasklogin:latest --no-cache --build-arg "BASE_IMG=pythonflasklogin:build" .
   ```

4. Start the services
   ```bash
   # start the database and the redis server
   sudo docker-compose up -d mariadb redis
   
   # the database need some time to initialize... 
   sleep 30
   
   # start the app, this will trigger sqlalchemy to create the tables in the database, afterwards the container is being stopped.
   sudo docker-compose up -d app
   
   function hash {
     python3 -c "from werkzeug import generate_password_hash; print(generate_password_hash(\"$1\"))"
   }
   function gen_uuid {
     if [[ -n $(which uuidgen) ]]; then
       uuidgen
     else
       python3 -c 'from uuid import uuid4; print(str(uuid4()))'
     fi
   }
   
   # create the default roles and one user
   sql="INSERT INTO example.role (id, name, description) VALUES (1, 'admin', 'Admin'), (2, 'user', 'User');"
   sudo docker-compose exec mariadb mysql -uroot -proot -sNe $sql
   sql="INSERT INTO example.user (guid, username, email, role, created, 2fa_enabled, password) \
    VALUES (\"$(gen_uuid)\", 'user', 'user2@example.com', 1, NOW(), 0, \"$(hash 'example')\");"
   sudo docker-compose exec mariadb mysql -uroot -proot -sNe $sql

   # now start the app for productive usage
   sudo docker-compose up -d app
   
   # show the status of the docker container
   sudo docker-compose ps
   ```
   
## Examples
![login page](../media/login.png?raw=true)
![setup page](../media/setup.png?raw=true)
![profile page](../media/profile.png?raw=true)