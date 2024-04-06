#!/bin/bash

# Create the database based on environment variable
echo "Checking if database $POSTGRES_DB exists"
if psql -U "$POSTGRES_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$POSTGRES_DB'" | grep -q 1; then
  echo "Database $POSTGRES_DB already exists"
else
  echo "Creating database $POSTGRES_DB"
  psql -U "$POSTGRES_USER" -c "CREATE DATABASE $POSTGRES_DB;"
  echo "Database $POSTGRES_DB created successfully"
fi
