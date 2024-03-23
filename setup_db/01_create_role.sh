#!/bin/bash

# Create postgres role based on environment variable
if psql -U postgres -c "SELECT rolname FROM pg_roles" | grep -qw "$PGUSER"; then
  echo "Role $PGUSER already exists"
else
  psql -U postgres -c "CREATE ROLE $PGUSER WITH LOGIN PASSWORD '$POSTGRES_PASSWORD';"
  echo "Role $PGUSER created successfully"
fi
