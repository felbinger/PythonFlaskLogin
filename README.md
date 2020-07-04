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
    curl -L "https://github.com/docker/compose/releases/download/1.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ```
   
3. Start the database (and redis) containers (`docker-compose up -d mariadb redis`)

4. Create the default roles and create a user
   ```bash
   sudo docker-compose exec mariadb mysql -uroot -sNe "INSERT INTO `role` (`id`, `name`, `description`) VALUES (1, 'admin', 'Admin'), (2, 'user', 'User');"
   sudo docker-compose exec mariadb mysql -uroot -sNe " \
    INSERT INTO example.user (guid, username, email, role, created, 2fa_enabled, password) VALUES \
    (\"$(python3 -c 'from uuid import uuid4; print(str(uuid4()))')\", 'user', 'user2@example.com', 1, NOW(), 0, \
    \"$(python3 -c 'from werkzeug import generate_password_hash; print(generate_password_hash("example"))')\");"
   ```
 
5. Start the application (`sudo docker-compose up -d app`)