#!/bin/bash
#set -e

secret=`python scripts/chainlit_secret`

export CHAINLIT_AUTH_SECRET="$secret"

# Path to the database file
DB_PATH="/sqlite/chainlit.db"

# Check if the chainlit.db file exists
if [ ! -f "$DB_PATH" ]; then
    echo "$DB_PATH not found. Running gen_db..."
    # Run the gen_db script to initialize the database
    ./scripts/gen_db $DB_PATH
else
    echo "$DB_PATH found. Skipping database initialization."
fi

# Run the application
echo "Starting Chainlit..."
chainlit run src/core/app.py --host 0.0.0.0

