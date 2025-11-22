#!/bin/bash
# Databricks Apps startup script with dynamic port configuration
# This script reads the port from environment variables to avoid 502 errors

# Get port from environment variables
# Priority: DATABRICKS_APP_PORT > PORT > default 8080
PORT=${DATABRICKS_APP_PORT:-${PORT:-8080}}

echo "Starting Streamlit app on port $PORT"

# Start Streamlit with dynamic port
exec streamlit run app.py \
  --server.port=$PORT \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --browser.gatherUsageStats=false
