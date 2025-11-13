# E&C SOP Deviation Tracking Platform

A comprehensive Standard Operating Procedure (SOP) management and deviation tracking application built for Databricks Apps using Streamlit.

## 🎯 Overview

The E&C SOP End-To-End Management Platform streamlines the process of submitting, reviewing, and tracking Standard Operating Procedures (SOPs) across your organization. Built specifically for the E&C Policy Team, this application provides:

- **Streamlined SOP Submission**: Easy-to-use form with validation and file upload
- **Real-time Tracking**: Monitor submission status and deviations
- **Automated Compliance**: AI-powered compliance checking (ready for integration)
- **Comprehensive Analytics**: Insights into submission trends and review performance
- **Professional UI**: Clean, modern interface optimized for corporate use

## ✨ Features

### 1. Dashboard
- Landing page with key metrics and recent activity
- Quick access to SOP submission portal
- Status distribution visualization
- Performance metrics overview

### 2. Submit SOP
- Comprehensive submission form with validation
- File upload support (PDF/Word)
- Business justification and impact assessment fields
- Risk assessment and compliance checkboxes
- Auto-generated SOP IDs

### 3. Track Deviations
- Interactive data table with all SOP submissions
- Advanced filtering by status, reviewer, and department
- Search functionality
- Export to CSV capability
- Summary statistics for filtered data

### 4. Analytics & Reports
- Status distribution charts
- Submissions over time (with 7-day moving average)
- Review time by reviewer analysis
- Compliance flags distribution
- Department and priority breakdowns

### 5. How to Submit Guide
- Step-by-step submission instructions
- Comprehensive FAQ section
- Contact information
- Best practices and tips

## 📋 Prerequisites

- **Databricks Workspace**: AWS, Azure, or GCP
- **Access to Databricks Apps**: Required for deployment
- **Python 3.9+**: Pre-installed in Databricks
- **Required Packages**: Listed in `requirements.txt`

## 🚀 Quick Start

### Local Testing

1. **Clone or navigate to the repository**
   ```bash
   cd databricks-dash-app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Access the app**
   - Open your browser to `http://localhost:8501`

### Deployment to Databricks Apps

#### Method 1: Databricks UI (Recommended)

1. **Navigate to Databricks Workspace**
   ```
   Your Workspace → Apps → Create App
   ```

2. **Upload Files**
   - Upload all files from this directory
   - Databricks will automatically detect Streamlit

3. **Configure App**
   - **App Name**: `E&C SOP Management Platform`
   - **Source Files**: Point to `app.py`
   - **Configuration**: Use `app.yaml` for settings

4. **Deploy**
   - Click "Deploy"
   - Wait for the app to start (usually 2-3 minutes)
   - Access via the provided URL

#### Method 2: Databricks CLI

1. **Install Databricks CLI** (if not already installed)
   ```bash
   pip install databricks-cli
   ```

2. **Configure Authentication**
   ```bash
   databricks configure --token
   ```
   - Enter your Databricks workspace URL
   - Enter your personal access token

3. **Deploy the App**
   ```bash
   databricks apps create ec-sop-platform \
     --source-code-path . \
     --description "E&C SOP Management Platform" \
     --config-file app.yaml
   ```

4. **Check Deployment Status**
   ```bash
   databricks apps get ec-sop-platform
   ```

#### Method 3: Git Integration

1. **Push to Git Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: E&C SOP Management Platform"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Connect Databricks Repos**
   - Navigate to: `Databricks → Repos → Add Repo`
   - Enter your Git repository URL
   - Pull the latest code

3. **Deploy from Repos**
   - Right-click on `app.py` in the repo
   - Select "Deploy as Databricks App"
   - Follow the prompts

## 📁 Project Structure

```
databricks-dash-app/
├── app.py                      # Main Streamlit application (900+ lines)
├── app.yaml                    # Databricks deployment configuration
├── requirements.txt            # Python dependencies
├── databricks_config.py        # Databricks integration utilities
├── README.md                   # This file
└── .gitignore                  # Git ignore file
```

## 🗄️ Data Integration

### Current Implementation
- **Sample Data**: 50 realistic SOP records generated on app load
- **Session State**: Data persisted during user session
- **In-Memory Storage**: Perfect for demo and testing

### Production Integration with Delta Tables

Replace the sample data function with Delta Table queries:

```python
from pyspark.sql import SparkSession

@st.cache_data
def load_sop_data():
    """Load SOP data from Delta Table"""
    spark = SparkSession.builder.getOrCreate()
    df = spark.read.format("delta").table("sop_tracking.submissions")
    return df.toPandas()

# Update session state initialization
if 'sop_data' not in st.session_state:
    st.session_state.sop_data = load_sop_data()
```

### Setting Up Delta Tables

```sql
-- Create database
CREATE DATABASE IF NOT EXISTS sop_tracking;

-- Create submissions table
CREATE TABLE IF NOT EXISTS sop_tracking.submissions (
    sop_id STRING,
    title STRING,
    department STRING,
    submission_date DATE,
    status STRING,
    assigned_reviewer STRING,
    last_updated TIMESTAMP,
    review_time_days INT,
    compliance_flags INT,
    compliance_flag_details STRING,
    priority STRING,
    implementation_date DATE
)
USING DELTA
LOCATION '/mnt/sop-tracking/submissions';
```

## 🎨 Customization

### Branding

Update the sidebar logo by replacing the placeholder:

```python
# In app.py, sidebar section (around line 260)
st.sidebar.image("path/to/your/company/logo.png", use_container_width=True)
```

### Color Scheme

Modify the CSS variables in `app.py`:

```css
:root {
    --primary-blue: #YOUR_COLOR;
    --secondary-gray: #YOUR_COLOR;
    --success-green: #YOUR_COLOR;
    --warning-yellow: #YOUR_COLOR;
    --error-red: #YOUR_COLOR;
}
```

Or update `app.yaml` environment variables:

```yaml
env:
  - name: STREAMLIT_THEME_PRIMARY_COLOR
    value: "#YOUR_COLOR"
```

## 🔧 Configuration

### Environment Variables

Set these in Databricks App configuration:

```bash
# Database connection
DATABASE_NAME=sop_tracking
CATALOG_NAME=main

# File storage
FILE_STORAGE_PATH=/dbfs/FileStore/sop-documents/

# Email notifications (optional)
SMTP_SERVER=smtp.company.com
SMTP_PORT=587
FROM_EMAIL=noreply@company.com
```

### Databricks Secrets

Store sensitive data in Databricks Secrets:

```python
import databricks.sdk as db

# Access secrets
db_token = dbutils.secrets.get(scope="sop-app", key="database-token")
smtp_password = dbutils.secrets.get(scope="sop-app", key="smtp-password")
```

## 📊 Sample Data

The application generates 50 realistic SOP records with:
- **Statuses**: Pending, In Review, Approved, Rejected, Requires Changes
- **Date Range**: Last 6 months
- **Reviewers**: 6 different team members
- **Departments**: 8 different departments
- **Compliance Flags**: Realistic distribution based on status

## 🔐 Security & Authentication

### Current Implementation
- Uses Databricks workspace authentication
- Session-based data isolation

### Production Enhancements

```python
from databricks_config import get_config, check_permission

# Check user permissions
config = get_config()
current_user = config.get_current_user()

# Role-based access control
if check_permission('submit'):
    # Show submission form
    pass
else:
    st.error("You don't have permission to submit SOPs")
```

## 🧪 Testing

### Local Testing Checklist

- ✅ All pages load without errors
- ✅ Navigation works between all tabs
- ✅ Sample data generates correctly (50 records)
- ✅ Form validation works
- ✅ File upload accepts PDF/Word
- ✅ Filters work on tracking page
- ✅ Charts render correctly
- ✅ Export to CSV downloads

### Run Local Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py

# Test in browser
# Navigate through all pages and test functionality
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: App won't start in Databricks
- Check `requirements.txt` is present
- Verify `app.yaml` configuration
- Check Databricks cluster is running
- Review app logs in Databricks UI

**Issue**: Data not persisting
- This is expected in demo mode (session-based storage)
- For persistence, integrate with Delta Tables
- See "Data Integration" section above

**Issue**: Charts not displaying
- Ensure Plotly is installed (`pip install plotly`)
- Check browser console for JavaScript errors
- Try clearing browser cache

**Issue**: File uploads not working
- Verify file size is under 50MB
- Check file format (PDF or Word only)
- Ensure proper permissions in Databricks

## 📚 Additional Resources

- [Databricks Apps Documentation](https://docs.databricks.com/en/apps/index.html)
- [Streamlit Documentation](https://docs.streamlit.io)
- [Delta Lake Guide](https://docs.databricks.com/delta/index.html)
- [Plotly Documentation](https://plotly.com/python/)

## 🔄 Version History

### v1.0.0 (January 2025)
- ✅ Initial release
- ✅ Dashboard with key metrics
- ✅ SOP submission form with validation
- ✅ Tracking dashboard with filters
- ✅ Analytics with 6 visualizations
- ✅ Comprehensive how-to guide
- ✅ 50 sample records
- ✅ Professional UI with custom CSS
- ✅ Export to CSV functionality
- ✅ Responsive design

### Planned Enhancements (v2.0)
- Delta Table integration
- Email notifications
- Document version tracking
- Role-based access control
- SharePoint integration
- Bulk upload capability
- Advanced search with filters
- Automated compliance checking
- Comment/feedback system
- Mobile optimization

## 📞 Support

### For E&C Policy Team
- **Email**: ec-policy@company.com
- **Phone**: (555) 123-4567
- **Hours**: Monday-Friday, 9:00 AM - 5:00 PM EST

### For Technical Support
- **Email**: ec-support@company.com
- **Databricks Support**: support@databricks.com
- **Streamlit Community**: https://discuss.streamlit.io

## 📄 License

Internal use only - Company confidential

---

**Built with ❤️ for the E&C Policy Team**

**Powered by Databricks Apps and Streamlit**
