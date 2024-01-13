#!/bin/bash

# Create the database based on environment variable
if psql -U postgres -lqt | cut -d \| -f 1 | grep -qw "V"; then
  echo "Database $DB_NAME already exists"
else
  psql -U postgres -c "CREATE DATABASE $DB_NAME;"
  echo "Database $DB_NAME created successfully"
fi
