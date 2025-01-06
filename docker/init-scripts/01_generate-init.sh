#!/bin/bash

# Use environment variables to create SQL commands
cat <<EOF > /docker-entrypoint-initdb.d/02_init-auth-db.sql
-- Create a new user
CREATE USER ${POSTGRES_AUTH_USER} WITH PASSWORD '${POSTGRES_AUTH_PASSWORD}';

-- Create a new database
CREATE DATABASE ${POSTGRES_AUTH_DB};

-- Grant privileges on the new database to the new user
GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_AUTH_DB} TO ${POSTGRES_AUTH_USER};

-- Set new user as an owner of a new database
ALTER DATABASE ${POSTGRES_AUTH_DB} OWNER TO ${POSTGRES_AUTH_USER};
EOF
