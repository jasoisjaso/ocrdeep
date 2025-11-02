#!/bin/bash
# In a real application, you would add commands here to wait for the database
# and run database migrations.
# For example:
# flask db upgrade

gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()" --timeout 120
