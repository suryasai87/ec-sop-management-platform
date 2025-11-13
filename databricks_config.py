"""
Databricks-specific configuration and utilities
for E&C SOP Deviation Tracking Platform
"""

import os
from typing import Optional, Dict, Any
import streamlit as st

class DatabricksConfig:
    """Configuration manager for Databricks integration"""
    
    def __init__(self):
        self.database_name = os.getenv('DATABASE_NAME', 'sop_tracking')
        self.catalog_name = os.getenv('CATALOG_NAME', 'main')
        self.file_storage_path = os.getenv('FILE_STORAGE_PATH', '/dbfs/FileStore/sop-documents/')
        
    @property
    def full_table_path(self) -> str:
        """Returns fully qualified table name"""
        return f"{self.catalog_name}.{self.database_name}"
    
    def get_current_user(self) -> str:
        """Get current Databricks user"""
        try:
            # In Databricks environment
            import IPython
            context = IPython.get_ipython().user_ns.get('dbutils')
            if context:
                return context.notebook.entry_point.getDbutils() \
                    .notebook().getContext().userName().get()
        except:
            pass
        
        # Fallback for local testing
        return os.getenv('USER', 'test_user@company.com')
    
    def is_databricks_environment(self) -> bool:
        """Check if running in Databricks"""
        return 'DATABRICKS_RUNTIME_VERSION' in os.environ


class DataHandler:
    """Handle data operations with Delta Tables"""
    
    def __init__(self, config: DatabricksConfig):
        self.config = config
        self._spark = None
    
    @property
    def spark(self):
        """Lazy initialization of Spark session"""
        if self._spark is None:
            try:
                from pyspark.sql import SparkSession
                self._spark = SparkSession.builder.getOrCreate()
            except ImportError:
                st.warning("PySpark not available. Using sample data mode.")
                return None
        return self._spark
    
    def load_sop_submissions(self) -> Optional[Any]:
        """Load SOP submissions from Delta Table"""
        if not self.spark:
            return None
        
        try:
            table_path = f"{self.config.full_table_path}.submissions"
            df = self.spark.read.format("delta").table(table_path)
            return df.toPandas()
        except Exception as e:
            st.error(f"Error loading data from Delta Table: {e}")
            return None
    
    def save_sop_submission(self, submission_data: Dict[str, Any]) -> bool:
        """Save new SOP submission to Delta Table"""
        if not self.spark:
            return False
        
        try:
            from pyspark.sql import Row
            
            # Create DataFrame from submission
            row = Row(**submission_data)
            df = self.spark.createDataFrame([row])
            
            # Append to Delta Table
            table_path = f"{self.config.full_table_path}.submissions"
            df.write.format("delta").mode("append").saveAsTable(table_path)
            
            return True
        except Exception as e:
            st.error(f"Error saving submission: {e}")
            return False
    
    def update_sop_status(self, sop_id: str, new_status: str, 
                          reviewer_comment: Optional[str] = None) -> bool:
        """Update SOP status in Delta Table"""
        if not self.spark:
            return False
        
        try:
            from delta.tables import DeltaTable
            from datetime import datetime
            
            table_path = f"{self.config.full_table_path}.submissions"
            delta_table = DeltaTable.forName(self.spark, table_path)
            
            # Update status and last_updated timestamp
            update_dict = {
                "status": f"'{new_status}'",
                "last_updated": f"'{datetime.now().isoformat()}'"
            }
            
            # Add reviewer comment if provided
            if reviewer_comment:
                update_dict["reviewer_comments"] = f"array_append(reviewer_comments, '{reviewer_comment}')"
            
            delta_table.update(
                condition=f"sop_id = '{sop_id}'",
                set=update_dict
            )
            
            return True
        except Exception as e:
            st.error(f"Error updating status: {e}")
            return False
    
    def get_user_submissions(self, user_email: str) -> Optional[Any]:
        """Get submissions for a specific user"""
        if not self.spark:
            return None
        
        try:
            table_path = f"{self.config.full_table_path}.submissions"
            df = self.spark.read.format("delta").table(table_path)
            user_df = df.filter(df.submitter_email == user_email)
            return user_df.toPandas()
        except Exception as e:
            st.error(f"Error loading user submissions: {e}")
            return None


class FileStorageHandler:
    """Handle file uploads/downloads with DBFS"""
    
    def __init__(self, config: DatabricksConfig):
        self.config = config
        self.storage_path = config.file_storage_path
    
    def save_file(self, file_content: bytes, sop_id: str, 
                  filename: str, version: int = 1) -> str:
        """Save uploaded file to DBFS"""
        try:
            # Create directory if it doesn't exist
            dir_path = os.path.join(self.storage_path, sop_id)
            os.makedirs(dir_path, exist_ok=True)
            
            # Save file with version
            file_path = os.path.join(dir_path, f"v{version}_{filename}")
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            return file_path
        except Exception as e:
            st.error(f"Error saving file: {e}")
            return ""
    
    def get_file(self, file_path: str) -> Optional[bytes]:
        """Retrieve file from DBFS"""
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            st.error(f"Error retrieving file: {e}")
            return None
    
    def list_versions(self, sop_id: str) -> list:
        """List all versions of documents for an SOP"""
        try:
            dir_path = os.path.join(self.storage_path, sop_id)
            if os.path.exists(dir_path):
                return sorted(os.listdir(dir_path))
            return []
        except Exception as e:
            st.error(f"Error listing versions: {e}")
            return []


class RoleManager:
    """Manage user roles and permissions"""
    
    ROLES = {
        'admin': ['submit', 'review', 'approve', 'delete', 'view_all'],
        'reviewer': ['review', 'approve', 'view_all'],
        'submitter': ['submit', 'view_own'],
        'viewer': ['view_all']
    }
    
    def __init__(self, config: DatabricksConfig):
        self.config = config
        self._spark = None
    
    @property
    def spark(self):
        """Lazy initialization of Spark session"""
        if self._spark is None:
            try:
                from pyspark.sql import SparkSession
                self._spark = SparkSession.builder.getOrCreate()
            except ImportError:
                return None
        return self._spark
    
    def get_user_role(self, user_email: str) -> str:
        """Get role for a user"""
        if not self.spark:
            return 'viewer'  # Default fallback
        
        try:
            table_path = f"{self.config.full_table_path}.user_roles"
            df = self.spark.read.format("delta").table(table_path)
            role_df = df.filter(df.email == user_email)
            
            if role_df.count() > 0:
                return role_df.first()['role']
            else:
                return 'viewer'  # Default role
        except Exception as e:
            st.warning(f"Could not fetch user role: {e}")
            return 'viewer'
    
    def has_permission(self, user_email: str, permission: str) -> bool:
        """Check if user has specific permission"""
        role = self.get_user_role(user_email)
        return permission in self.ROLES.get(role, [])
    
    def assign_role(self, user_email: str, role: str) -> bool:
        """Assign role to user (admin only)"""
        if role not in self.ROLES:
            st.error(f"Invalid role: {role}")
            return False
        
        if not self.spark:
            return False
        
        try:
            from pyspark.sql import Row
            from delta.tables import DeltaTable
            
            table_path = f"{self.config.full_table_path}.user_roles"
            
            # Check if user already has a role
            delta_table = DeltaTable.forName(self.spark, table_path)
            
            # Upsert role
            new_data = self.spark.createDataFrame([
                Row(email=user_email, role=role, updated_at=datetime.now())
            ])
            
            delta_table.alias("target").merge(
                new_data.alias("source"),
                "target.email = source.email"
            ).whenMatchedUpdate(
                set={"role": "source.role", "updated_at": "source.updated_at"}
            ).whenNotMatchedInsert(
                values={
                    "email": "source.email",
                    "role": "source.role",
                    "updated_at": "source.updated_at"
                }
            ).execute()
            
            return True
        except Exception as e:
            st.error(f"Error assigning role: {e}")
            return False


class NotificationService:
    """Handle email notifications"""
    
    def __init__(self, config: DatabricksConfig):
        self.config = config
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.company.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@company.com')
    
    def send_submission_notification(self, sop_id: str, reviewer_email: str) -> bool:
        """Notify reviewer of new submission"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            
            subject = f"New SOP Submission: {sop_id}"
            body = f"""
            A new SOP has been submitted and assigned to you for review.
            
            SOP ID: {sop_id}
            
            Please log in to the SOP Management Platform to review this submission.
            
            Thank you,
            E&C Policy Team
            """
            
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = reviewer_email
            
            # Note: In production, use proper SMTP authentication
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                # server.login(username, password)  # Add credentials from secrets
                server.send_message(msg)
            
            return True
        except Exception as e:
            st.warning(f"Could not send notification: {e}")
            return False
    
    def send_status_update(self, sop_id: str, new_status: str, 
                          submitter_email: str) -> bool:
        """Notify submitter of status change"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            
            subject = f"SOP Status Update: {sop_id}"
            body = f"""
            Your SOP submission status has been updated.
            
            SOP ID: {sop_id}
            New Status: {new_status}
            
            Log in to the SOP Management Platform for more details.
            
            Thank you,
            E&C Policy Team
            """
            
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = submitter_email
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.send_message(msg)
            
            return True
        except Exception as e:
            st.warning(f"Could not send notification: {e}")
            return False


# Helper functions for Streamlit integration

@st.cache_resource
def get_config() -> DatabricksConfig:
    """Get cached Databricks configuration"""
    return DatabricksConfig()

@st.cache_resource
def get_data_handler() -> DataHandler:
    """Get cached data handler"""
    config = get_config()
    return DataHandler(config)

@st.cache_resource
def get_role_manager() -> RoleManager:
    """Get cached role manager"""
    config = get_config()
    return RoleManager(config)

def check_permission(permission: str) -> bool:
    """Check if current user has permission"""
    config = get_config()
    role_manager = get_role_manager()
    current_user = config.get_current_user()
    
    return role_manager.has_permission(current_user, permission)

def require_permission(permission: str):
    """Decorator to require permission for a function"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not check_permission(permission):
                st.error(f"You don't have permission to perform this action. Required: {permission}")
                st.stop()
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Usage example in main app:
"""
from config.databricks_config import (
    get_config, get_data_handler, get_role_manager, 
    check_permission, require_permission
)

# In your Streamlit app
config = get_config()
data_handler = get_data_handler()

# Check if user can submit
if check_permission('submit'):
    # Show submission form
    pass

# Protect admin functions
@require_permission('approve')
def approve_sop(sop_id):
    # Approval logic here
    pass
"""
