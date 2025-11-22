# Deployment Notes - Dynamic Port Configuration

## Summary of Changes

This repository has been updated to use **dynamic port configuration** to prevent 502 Bad Gateway errors when deploying to Databricks Apps.

## What Changed

### 1. New File: `start.sh`
- **Purpose**: Startup script that reads port from environment variables
- **Logic**:
  - Checks `DATABRICKS_APP_PORT` first (Databricks Apps standard)
  - Falls back to `PORT` if not set
  - Defaults to `8080` if neither is set
- **Usage**: Called by `app.yaml` to start the Streamlit application

```bash
#!/bin/bash
# Get port from environment variables
PORT=${DATABRICKS_APP_PORT:-${PORT:-8080}}

echo "Starting Streamlit app on port $PORT"

exec streamlit run app.py \
  --server.port=$PORT \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --browser.gatherUsageStats=false
```

### 2. Updated: `app.yaml`
**Before:**
```yaml
command:
  - streamlit
  - run
  - app.py
  - --server.port=8080  # ❌ Hardcoded port
  - --server.address=0.0.0.0
```

**After:**
```yaml
command:
  - /bin/bash
  - start.sh  # ✅ Dynamic port configuration
```

### 3. Updated: `README.md`
- Added `start.sh` to project structure
- Documented the dynamic port configuration
- Added troubleshooting section for 502 errors
- Updated deployment instructions

## Why This Matters

### Problem with Hardcoded Ports
When deploying Databricks Apps, the platform assigns dynamic ports to each application instance. Using a hardcoded port (like `8080`) can cause:
- **502 Bad Gateway errors**: The app binds to wrong port
- **Deployment failures**: Port conflicts with platform expectations
- **Inconsistent behavior**: Works in some workspaces but not others

### Solution: Dynamic Port Reading
By reading the port from environment variables:
- ✅ Works in **any Databricks workspace**
- ✅ No port conflicts
- ✅ Follows Databricks Apps best practices
- ✅ Portable across environments (dev, staging, prod)

## Deployment Instructions

### For New Deployments

1. **Clone the repository**
   ```bash
   git clone https://github.com/suryasai87/ec-sop-management-platform.git
   cd ec-sop-management-platform
   ```

2. **Ensure start.sh is executable**
   ```bash
   chmod +x start.sh
   ```

3. **Deploy using Databricks CLI**
   ```bash
   databricks apps create ec-sop-platform \
     --source-code-path . \
     --description "E&C SOP Management Platform" \
     --config-file app.yaml
   ```

4. **Verify deployment**
   ```bash
   databricks apps get ec-sop-platform
   ```

### For Existing Deployments

If you have an existing deployment with the old hardcoded port:

1. **Pull latest changes**
   ```bash
   cd ec-sop-management-platform
   git pull origin main
   ```

2. **Make start.sh executable**
   ```bash
   chmod +x start.sh
   ```

3. **Redeploy the app**
   ```bash
   # Option 1: Hard redeploy (recommended)
   databricks apps delete ec-sop-platform
   databricks apps create ec-sop-platform \
     --source-code-path . \
     --config-file app.yaml

   # Option 2: Update existing
   databricks apps deploy ec-sop-platform --source-code-path .
   ```

## Verification

After deployment, check the app logs to confirm it's using the correct port:

```bash
databricks apps logs ec-sop-platform
```

You should see:
```
Starting Streamlit app on port [DYNAMIC_PORT]
```

## Environment Variables

The app automatically detects and uses these environment variables (in order of priority):

1. `DATABRICKS_APP_PORT` - Set by Databricks Apps platform
2. `PORT` - Generic port variable
3. `8080` - Default fallback

You typically don't need to set these manually - Databricks handles it automatically.

## Rollback (If Needed)

If you need to rollback to the old configuration:

```bash
git checkout [previous-commit-hash] app.yaml
# Remove start.sh if needed
rm start.sh
git commit -m "Rollback to hardcoded port"
git push
```

**Note**: Rolling back is not recommended as it will reintroduce the 502 error issue.

## Testing Locally

The dynamic port configuration also works for local testing:

```bash
# Default port (8080)
./start.sh

# Custom port
PORT=8501 ./start.sh

# Databricks-style port
DATABRICKS_APP_PORT=9000 ./start.sh
```

## Related Files

- `start.sh` - Startup script with port logic
- `app.yaml` - Databricks deployment configuration
- `README.md` - Full project documentation
- `DEPLOYMENT_INFO.md` - Detailed deployment guide

## Support

If you encounter issues with port configuration:

1. Check app logs: `databricks apps logs ec-sop-platform`
2. Verify `start.sh` permissions: `ls -la start.sh`
3. Review app.yaml configuration
4. Contact: ec-support@company.com

---

**Last Updated**: January 2025
**Version**: 1.1.0 (Dynamic Port Configuration)
