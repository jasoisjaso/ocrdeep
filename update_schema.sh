#!/bin/sh
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    ALTER TABLE users ALTER COLUMN password_hash TYPE VARCHAR(256);
EOSQL
