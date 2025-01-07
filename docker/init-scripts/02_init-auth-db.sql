-- Create a new user
CREATE USER artadas_auth_db_user WITH PASSWORD 'artadas_auth_db_password';

-- Create a new database
CREATE DATABASE artadas_auth_db;

-- Grant privileges on the new database to the new user
GRANT ALL PRIVILEGES ON DATABASE artadas_auth_db TO artadas_auth_db_user;

-- Set new user as an owner of a new database
ALTER DATABASE artadas_auth_db OWNER TO artadas_auth_db_user;
