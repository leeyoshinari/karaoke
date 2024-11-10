#!/bin/bash
DATABASE_FILE="/KTV/sqlite3.db"
if [ ! -f "$DATABASE_FILE" ]; then
  aerich init -t settings.TORTOISE_ORM
  aerich init-db
else
  echo "Database file found. Skipping initialization."
fi
exec "$@"
