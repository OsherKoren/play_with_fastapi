#!/bin/bash

# Create the database based on environment variable
if psql -U "$POSTGRES_USER" -lqt | cut -d \| -f 1 | grep -qw "V"; then
  echo "Database $POSTGRES_DB already exists"
else
  psql -U "$POSTGRES_USER" -c "CREATE DATABASE $POSTGRES_DB;"
  echo "Database $POSTGRES_DB created successfully"
fi
