#!/bin/bash

# Create the database based on environment variable
if psql -U $PGUSER -lqt | cut -d \| -f 1 | grep -qw "V"; then
  echo "Database $PGDATABASE already exists"
else
  psql -U $PGUSER -c "CREATE DATABASE $PGDATABASE;"
  echo "Database $PGDATABASE created successfully"
fi
