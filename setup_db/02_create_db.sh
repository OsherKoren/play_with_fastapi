#!/bin/bash

# Create the database based on environment variable
if psql -U "$POSTGRES_USER" -lqt | cut -d \| -f 1 | grep -qw "$POSTGRES_DB"; then
  echo "Database $POSTGRES_DB already exists"
else
  echo "Creating database $POSTGRES_DB"
  psql -U "$POSTGRES_USER" -c "CREATE DATABASE $POSTGRES_DB;"
  echo "Database $POSTGRES_DB created successfully"
fi
