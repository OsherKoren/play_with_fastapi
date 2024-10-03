#!/bin/bash

# Create postgres db role based on environment variable
if psql -U postgres -c "SELECT rolname FROM pg_roles" | grep -qw "$POSTGRES_USER"; then
  echo "Role $POSTGRES_USER already exists"
else
  psql -U postgres -c "CREATE ROLE $POSTGRES_USER WITH LOGIN PASSWORD '$POSTGRES_PASSWORD';"
  echo "Role $POSTGRES_USER created successfully"
fi
