#!/bin/bash

# Initialize PostgreSQL database for No Pressure app

set -e

DB_NAME="nopressure"

echo "Initializing database: $DB_NAME"

# Create database if it doesn't exist
psql -d postgres -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || \
    echo "Database $DB_NAME already exists or creation failed"

# Create bp_readings table
psql -d "$DB_NAME" <<EOF
CREATE TABLE IF NOT EXISTS bp_readings (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sys INTEGER NOT NULL,
    dia INTEGER NOT NULL,
    hr INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_bp_readings_timestamp ON bp_readings(timestamp DESC);

EOF

echo "Database initialized successfully!"
echo "Table bp_readings created with columns: id, timestamp, sys, dia, hr"

