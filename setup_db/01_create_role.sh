#!/bin/bash

# Create postgres role based on environment variable
if psql -U postgres -c "SELECT rolname FROM pg_roles" | grep -qw "$PS_USER"; then
  echo "Role $PS_USER already exists"
else
  psql -U postgres -c "CREATE ROLE $PS_USER WITH LOGIN PASSWORD '$PS_PASSWORD';"
  echo "Role $PS_USER created successfully"
fi
