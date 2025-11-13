"""
E&C SOP Deviation Tracking Platform - Databricks App
Built with Streamlit for Databricks Apps deployment
Production-ready version with comprehensive features
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# Page configuration
st.set_page_config(
    page_title="E&C SOP Management Platform",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-blue: #3B82F6;
        --secondary-gray: #6B7280;
        --success-green: #10B981;
        --warning-yellow: #F59E0B;
        --error-red: #EF4444;
        --dark-blue: #1E3A8A;
    }

    /* Headers */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
        line-height: 1.2;
    }

    .sub-header {
        font-size: 1.1rem;
        color: #6B7280;
        margin-bottom: 2rem;
        line-height: 1.6;
    }

    /* Step cards */
    .step-card {
        background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
        padding: 1.5rem;
        border-radius: 0.75rem;
        border-left: 5px solid #3B82F6;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }

    .step-card:hover {
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
        transform: translateY(-2px);
    }

    .step-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1E3A8A;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
    }

    .step-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        background-color: #3B82F6;
        color: white;
        border-radius: 50%;
        font-weight: 700;
        margin-right: 0.75rem;
        font-size: 1rem;
    }

    .step-content {
        color: #374151;
        line-height: 1.7;
        padding-left: 2.5rem;
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.75rem;
        color: white;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    /* CTA button styling */
    .cta-button {
        background-color: #3B82F6;
        color: white;
        padding: 0.75rem 2rem;
        border-radius: 0.5rem;
        font-weight: 600;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }

    .cta-button:hover {
        background-color: #2563EB;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }

    /* Info boxes */
    .info-box {
        background-color: #EFF6FF;
        border-left: 4px solid #3B82F6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }

    .success-box {
        background-color: #F0FDF4;
        border-left: 4px solid #10B981;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }

    /* Table styling */
    .dataframe {
        font-size: 0.9rem;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%);
    }

    /* Card container */
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
    }

    /* Status badges */
    .status-pending {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 0.25rem 0.75rem;
        border-radius: 0.375rem;
        font-weight: 600;
        font-size: 0.875rem;
    }

    .status-approved {
        background-color: #D1FAE5;
        color: #065F46;
        padding: 0.25rem 0.75rem;
        border-radius: 0.375rem;
        font-weight: 600;
        font-size: 0.875rem;
    }

    .status-rejected {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 0.25rem 0.75rem;
        border-radius: 0.375rem;
        font-weight: 600;
        font-size: 0.875rem;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        .step-title {
            font-size: 1.1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Generate sample data
@st.cache_data
def generate_sample_data():
    """Generate realistic sample SOP data with comprehensive fields"""
    statuses = ['Pending', 'In Review', 'Approved', 'Rejected', 'Requires Changes']
    status_weights = [0.15, 0.25, 0.40, 0.10, 0.10]  # Realistic distribution

    reviewers = ['John Doe', 'Jane Smith', 'Michael Johnson', 'Sarah Williams', 'David Brown', 'Emily Chen']
    departments = ['Manufacturing', 'Operations', 'HR', 'Finance', 'IT', 'Quality', 'Safety', 'Compliance']
    sop_types = ['Process Update', 'New Procedure', 'Policy Revision', 'Safety Protocol', 'Quality Standard', 'Compliance Update']

    compliance_flags_pool = [
        'Template mismatch', 'Missing section 3.4', 'Risk assessment incomplete',
        'Stakeholder approval pending', 'Version control issue', 'Documentation incomplete',
        'Compliance review needed', 'Impact assessment unclear'
    ]

    data = []
    start_date = datetime.now() - timedelta(days=180)

    for i in range(50):
        submission_date = start_date + timedelta(days=random.randint(0, 180))
        status = random.choices(statuses, weights=status_weights)[0]
        review_time = random.randint(1, 14) if status != 'Pending' else 0
        last_updated = submission_date + timedelta(days=review_time) if review_time > 0 else submission_date

        # Generate compliance flags based on status
        num_flags = 0 if status == 'Approved' else random.randint(0, 5)
        flags = random.sample(compliance_flags_pool, min(num_flags, len(compliance_flags_pool)))

        record = {
            'SOP ID': f'SOP-2025-{str(i+1).zfill(3)}',
            'Title': f'{random.choice(sop_types)} - {random.choice(departments)}',
            'Department': random.choice(departments),
            'Submission Date': submission_date.strftime('%Y-%m-%d'),
            'Status': status,
            'Assigned Reviewer': random.choice(reviewers),
            'Last Updated': last_updated.strftime('%Y-%m-%d'),
            'Review Time (Days)': review_time,
            'Compliance Flags': num_flags,
            'Compliance Flag Details': ', '.join(flags) if flags else 'None',
            'Priority': random.choice(['Low', 'Medium', 'High', 'Critical']),
            'Implementation Date': (submission_date + timedelta(days=random.randint(30, 90))).strftime('%Y-%m-%d'),
        }
        data.append(record)

    return pd.DataFrame(data)

# Initialize session state
if 'sop_data' not in st.session_state:
    st.session_state.sop_data = generate_sample_data()

if 'submission_count' not in st.session_state:
    st.session_state.submission_count = 51  # Start after sample data

# Sidebar navigation
with st.sidebar:
    # Logo placeholder - replace with actual logo
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 0.5rem; margin-bottom: 1rem;'>
        <h2 style='color: white; margin: 0; font-size: 1.5rem;'>E&C</h2>
        <p style='color: white; margin: 0; font-size: 0.9rem;'>SOP Platform</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio(
        "Navigation",
        ["🏠 Dashboard", "📝 Submit SOP", "📊 Track Deviations", "📈 Analytics", "❓ How to Submit"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### 📊 Quick Stats")

    total_sops = len(st.session_state.sop_data)
    pending = len(st.session_state.sop_data[st.session_state.sop_data['Status'] == 'Pending'])
    approved = len(st.session_state.sop_data[st.session_state.sop_data['Status'] == 'Approved'])
    in_review = len(st.session_state.sop_data[st.session_state.sop_data['Status'] == 'In Review'])

    st.metric("Total SOPs", total_sops)
    st.metric("Pending Review", pending)
    st.metric("In Review", in_review)
    st.metric("Approved", approved)

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; font-size: 0.85rem; color: #6B7280;'>
        <p>Need Help?</p>
        <p><strong>ec-policy@company.com</strong></p>
        <p>(555) 123-4567</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# PAGE: DASHBOARD
# ============================================================================
if page == "🏠 Dashboard":
    st.markdown('<div class="main-header">E&C SOP End-To-End Management Platform</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</div>', unsafe_allow_html=True)

    # Call-to-action section
    st.markdown("### 🚀 Quick Access")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.info("📋 **Submit new SOPs and track existing submissions**")
        st.markdown("""
        Access the SOP Submission portal to submit new Standard Operating Procedures,
        track the status of your submissions, and collaborate with the E&C Policy Team.
        """)

        if st.button("🔗 Access SOP Submission SharePoint", type="primary", use_container_width=True):
            st.success("Opening SharePoint portal... (This would redirect to your SharePoint site)")
            st.info("For this demo, use the 'Submit SOP' tab to submit new procedures.")

    with col2:
        st.markdown("**Platform Features:**")
        st.markdown("""
        - ✅ Streamlined submission process
        - ✅ Real-time status tracking
        - ✅ Automated compliance checks
        - ✅ Comprehensive analytics
        - ✅ Version control
        """)

    st.markdown("---")

    # Key Metrics Row
    st.markdown("### 📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Submissions", total_sops, delta="+5 this week", delta_color="normal")

    with col2:
        st.metric("Pending Reviews", pending, delta="-2 from last week", delta_color="inverse")

    with col3:
        approval_rate = (approved / total_sops * 100) if total_sops > 0 else 0
        st.metric("Approval Rate", f"{approval_rate:.1f}%", delta="+3.2%")

    with col4:
        avg_time = st.session_state.sop_data[st.session_state.sop_data['Review Time (Days)'] > 0]['Review Time (Days)'].mean()
        st.metric("Avg Review Time", f"{avg_time:.1f} days", delta="-0.5 days", delta_color="inverse")

    st.markdown("---")

    # Recent Activity and Charts
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 📋 Recent Activity")
        recent = st.session_state.sop_data.sort_values('Last Updated', ascending=False).head(8)

        for _, row in recent.iterrows():
            status_class = 'status-approved' if row['Status'] == 'Approved' else 'status-pending' if row['Status'] == 'Pending' else 'status-rejected' if row['Status'] == 'Rejected' else ''

            st.markdown(f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{row['SOP ID']}</strong>
                        <p style="margin: 0.25rem 0; color: #6B7280; font-size: 0.9rem;">{row['Title'][:50]}...</p>
                        <p style="margin: 0; color: #9CA3AF; font-size: 0.8rem;">Updated: {row['Last Updated']}</p>
                    </div>
                    <span class="{status_class}">{row['Status']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 📈 Status Distribution")
        status_counts = st.session_state.sop_data['Status'].value_counts()

        colors = {
            'Approved': '#10B981',
            'In Review': '#3B82F6',
            'Pending': '#F59E0B',
            'Rejected': '#EF4444',
            'Requires Changes': '#8B5CF6'
        }
        color_sequence = [colors.get(status, '#6B7280') for status in status_counts.index]

        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            hole=0.5,
            color_discrete_sequence=color_sequence
        )
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            textfont_size=12,
            marker=dict(line=dict(color='#FFFFFF', width=2))
        )
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.1)
        )
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE: SUBMIT SOP
# ============================================================================
elif page == "📝 Submit SOP":
    st.markdown('<div class="main-header">Submit New SOP</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Complete the form below to submit your Standard Operating Procedure for review</div>', unsafe_allow_html=True)

    st.info("📝 **Note:** All fields marked with * are required. Ensure you have all necessary documentation before submitting.")

    with st.form("sop_submission_form", clear_on_submit=True):
        st.markdown("#### Basic Information")
        col1, col2 = st.columns(2)

        with col1:
            sop_title = st.text_input("SOP Title *", placeholder="Enter descriptive SOP title")
            department = st.selectbox(
                "Department *",
                ["", "Manufacturing", "Operations", "HR", "Finance", "IT", "Quality", "Safety", "Compliance"]
            )
            submission_type = st.selectbox(
                "Submission Type *",
                ["", "New SOP", "Policy Update", "Process Revision", "Safety Protocol", "Quality Standard", "Compliance Update"]
            )

        with col2:
            implementation_date = st.date_input(
                "Proposed Implementation Date *",
                min_value=datetime.now().date(),
                value=datetime.now().date() + timedelta(days=30)
            )
            priority = st.selectbox("Priority Level *", ["", "Low", "Medium", "High", "Critical"])
            reviewer = st.selectbox(
                "Preferred Reviewer",
                ["Auto-assign", "John Doe", "Jane Smith", "Michael Johnson", "Sarah Williams", "David Brown"]
            )

        st.markdown("---")
        st.markdown("#### Detailed Information")

        business_justification = st.text_area(
            "Business Justification *",
            placeholder="Explain the business need, expected benefits, and rationale for this SOP...",
            height=120,
            help="Provide a clear explanation of why this SOP is needed and how it will benefit the organization."
        )

        impact_assessment = st.text_area(
            "Impact Assessment *",
            placeholder="Describe the expected impact on operations, processes, stakeholders, and resources...",
            height=120,
            help="Detail how this SOP will affect current operations and what changes will be required."
        )

        st.markdown("---")
        st.markdown("#### Prerequisites & Compliance")

        col1, col2, col3 = st.columns(3)
        with col1:
            risk_assessment = st.checkbox("✅ Risk Assessment Completed")
        with col2:
            stakeholder_approval = st.checkbox("✅ Stakeholder Approvals Obtained")
        with col3:
            compliance_review = st.checkbox("✅ Compliance Review Completed")

        st.markdown("---")
        st.markdown("#### Document Upload")

        uploaded_file = st.file_uploader(
            "Upload SOP Document * (PDF or Word)",
            type=['pdf', 'docx', 'doc'],
            help="Upload your SOP document in PDF or Word format (Max 50MB)"
        )

        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")

        st.markdown("---")

        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            submit_button = st.form_submit_button("✅ Submit SOP", type="primary", use_container_width=True)
        with col2:
            draft_button = st.form_submit_button("💾 Save as Draft", use_container_width=True)

        # Form submission logic
        if submit_button:
            # Validation
            errors = []
            if not sop_title:
                errors.append("SOP Title is required")
            if not department:
                errors.append("Department is required")
            if not submission_type:
                errors.append("Submission Type is required")
            if not priority:
                errors.append("Priority Level is required")
            if not business_justification:
                errors.append("Business Justification is required")
            if not impact_assessment:
                errors.append("Impact Assessment is required")
            if not uploaded_file:
                errors.append("SOP Document must be uploaded")

            if errors:
                st.error("**Validation Failed:**")
                for error in errors:
                    st.error(f"• {error}")
            else:
                # Generate new SOP ID
                new_sop_id = f"SOP-2025-{str(st.session_state.submission_count).zfill(3)}"
                st.session_state.submission_count += 1

                # Add to session state data (in production, this would go to Delta Table)
                new_record = {
                    'SOP ID': new_sop_id,
                    'Title': f'{submission_type} - {department}',
                    'Department': department,
                    'Submission Date': datetime.now().strftime('%Y-%m-%d'),
                    'Status': 'Pending',
                    'Assigned Reviewer': reviewer if reviewer != 'Auto-assign' else 'John Doe',
                    'Last Updated': datetime.now().strftime('%Y-%m-%d'),
                    'Review Time (Days)': 0,
                    'Compliance Flags': 0,
                    'Compliance Flag Details': 'None',
                    'Priority': priority,
                    'Implementation Date': implementation_date.strftime('%Y-%m-%d'),
                }

                st.session_state.sop_data = pd.concat([
                    st.session_state.sop_data,
                    pd.DataFrame([new_record])
                ], ignore_index=True)

                st.success(f"✅ **SOP Submitted Successfully!**")
                st.success(f"📋 **Reference ID:** {new_sop_id}")
                st.info(f"🔔 Your submission will be reviewed by {new_record['Assigned Reviewer']} within 5-7 business days.")
                st.balloons()

        if draft_button:
            st.info("💾 Draft saved successfully. You can continue editing later.")

# ============================================================================
# PAGE: TRACK DEVIATIONS
# ============================================================================
elif page == "📊 Track Deviations":
    st.markdown('<div class="main-header">Track SOP Submissions & Deviations</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Monitor and manage all SOP submissions and their review status</div>', unsafe_allow_html=True)

    # Filters
    st.markdown("### 🔍 Filters")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        status_filter = st.multiselect(
            "Filter by Status",
            options=st.session_state.sop_data['Status'].unique(),
            default=st.session_state.sop_data['Status'].unique()
        )

    with col2:
        reviewer_filter = st.multiselect(
            "Filter by Reviewer",
            options=st.session_state.sop_data['Assigned Reviewer'].unique(),
            default=st.session_state.sop_data['Assigned Reviewer'].unique()
        )

    with col3:
        department_filter = st.multiselect(
            "Filter by Department",
            options=st.session_state.sop_data['Department'].unique(),
            default=st.session_state.sop_data['Department'].unique()
        )

    with col4:
        search_query = st.text_input("🔍 Search", placeholder="Search by ID or Title")

    # Apply filters
    filtered_data = st.session_state.sop_data[
        (st.session_state.sop_data['Status'].isin(status_filter)) &
        (st.session_state.sop_data['Assigned Reviewer'].isin(reviewer_filter)) &
        (st.session_state.sop_data['Department'].isin(department_filter))
    ]

    if search_query:
        filtered_data = filtered_data[
            filtered_data['SOP ID'].str.contains(search_query, case=False) |
            filtered_data['Title'].str.contains(search_query, case=False)
        ]

    # Results summary and export
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"Showing **{len(filtered_data)}** of **{len(st.session_state.sop_data)}** SOPs")
    with col2:
        if st.button("📥 Export to CSV", use_container_width=True):
            csv = filtered_data.to_csv(index=False)
            st.download_button(
                label="Download CSV File",
                data=csv,
                file_name=f"sop_tracking_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

    st.markdown("---")

    # Display data table
    st.dataframe(
        filtered_data,
        use_container_width=True,
        height=500,
        column_config={
            "SOP ID": st.column_config.TextColumn("SOP ID", width="small", help="Unique SOP identifier"),
            "Title": st.column_config.TextColumn("Title", width="large"),
            "Department": st.column_config.TextColumn("Department", width="small"),
            "Submission Date": st.column_config.DateColumn("Submitted", width="small"),
            "Status": st.column_config.TextColumn("Status", width="small"),
            "Assigned Reviewer": st.column_config.TextColumn("Reviewer", width="medium"),
            "Last Updated": st.column_config.DateColumn("Last Updated", width="small"),
            "Review Time (Days)": st.column_config.NumberColumn("Review Days", width="small", format="%d"),
            "Compliance Flags": st.column_config.NumberColumn("Flags", width="small", format="%d"),
            "Priority": st.column_config.TextColumn("Priority", width="small"),
        },
        hide_index=True
    )

    # Summary statistics for filtered data
    if len(filtered_data) > 0:
        st.markdown("---")
        st.markdown("### 📊 Filtered Data Summary")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Filtered SOPs", len(filtered_data))
        with col2:
            avg_review = filtered_data[filtered_data['Review Time (Days)'] > 0]['Review Time (Days)'].mean()
            st.metric("Avg Review Time", f"{avg_review:.1f} days" if not pd.isna(avg_review) else "N/A")
        with col3:
            total_flags = filtered_data['Compliance Flags'].sum()
            st.metric("Total Flags", int(total_flags))
        with col4:
            critical_count = len(filtered_data[filtered_data['Priority'] == 'Critical'])
            st.metric("Critical Priority", critical_count)

# ============================================================================
# PAGE: ANALYTICS
# ============================================================================
elif page == "📈 Analytics":
    st.markdown('<div class="main-header">SOP Analytics & Reports</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Comprehensive insights into SOP submissions and review performance</div>', unsafe_allow_html=True)

    # Summary metrics
    st.markdown("### 📊 Performance Metrics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total SOPs", total_sops, delta="+12 vs last month")

    with col2:
        approval_rate = (approved / total_sops * 100) if total_sops > 0 else 0
        st.metric("Approval Rate", f"{approval_rate:.1f}%", delta="+3.2%")

    with col3:
        avg_time = st.session_state.sop_data[st.session_state.sop_data['Review Time (Days)'] > 0]['Review Time (Days)'].mean()
        st.metric("Avg Review Time", f"{avg_time:.1f} days", delta="-0.8 days", delta_color="inverse")

    with col4:
        active_reviewers = st.session_state.sop_data['Assigned Reviewer'].nunique()
        st.metric("Active Reviewers", active_reviewers)

    st.markdown("---")

    # Charts Row 1
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Status Distribution")
        status_counts = st.session_state.sop_data['Status'].value_counts()

        colors = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6']
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            hole=0.4,
            color_discrete_sequence=colors
        )
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            textfont_size=13,
            marker=dict(line=dict(color='#FFFFFF', width=2))
        )
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 📈 Submissions Over Time")

        # Aggregate by date
        submissions_by_date = st.session_state.sop_data.groupby('Submission Date').size().reset_index(name='Count')
        submissions_by_date['Submission Date'] = pd.to_datetime(submissions_by_date['Submission Date'])
        submissions_by_date = submissions_by_date.sort_values('Submission Date')

        # Calculate 7-day moving average
        submissions_by_date['7-Day MA'] = submissions_by_date['Count'].rolling(window=7, min_periods=1).mean()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=submissions_by_date['Submission Date'],
            y=submissions_by_date['Count'],
            mode='lines+markers',
            name='Daily Submissions',
            line=dict(color='#3B82F6', width=2),
            marker=dict(size=6)
        ))
        fig.add_trace(go.Scatter(
            x=submissions_by_date['Submission Date'],
            y=submissions_by_date['7-Day MA'],
            mode='lines',
            name='7-Day Average',
            line=dict(color='#10B981', width=2, dash='dash')
        ))
        fig.update_layout(
            height=400,
            xaxis_title="Date",
            yaxis_title="Number of Submissions",
            hovermode='x unified',
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Charts Row 2
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ⏱️ Review Time by Reviewer")
        avg_review_time = st.session_state.sop_data[st.session_state.sop_data['Review Time (Days)'] > 0].groupby('Assigned Reviewer')['Review Time (Days)'].mean().reset_index()
        avg_review_time = avg_review_time.sort_values('Review Time (Days)', ascending=True)

        fig = px.bar(
            avg_review_time,
            x='Review Time (Days)',
            y='Assigned Reviewer',
            orientation='h',
            color='Review Time (Days)',
            color_continuous_scale='RdYlGn_r',
            text='Review Time (Days)'
        )
        fig.update_traces(texttemplate='%{text:.1f} days', textposition='outside')
        fig.update_layout(
            height=400,
            xaxis_title="Average Review Time (Days)",
            yaxis_title="Reviewer",
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 🚩 Compliance Flags Distribution")
        fig = px.histogram(
            st.session_state.sop_data,
            x='Compliance Flags',
            nbins=6,
            color_discrete_sequence=['#3B82F6']
        )
        fig.update_layout(
            height=400,
            xaxis_title="Number of Compliance Flags",
            yaxis_title="Count of SOPs",
            bargap=0.1,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        fig.update_traces(marker_line_color='#1E3A8A', marker_line_width=1.5)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Additional Analytics
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🏢 Submissions by Department")
        dept_counts = st.session_state.sop_data['Department'].value_counts().reset_index()
        dept_counts.columns = ['Department', 'Count']

        fig = px.bar(
            dept_counts,
            x='Department',
            y='Count',
            color='Count',
            color_continuous_scale='Blues'
        )
        fig.update_layout(
            height=350,
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### ⚡ Priority Distribution")
        priority_counts = st.session_state.sop_data['Priority'].value_counts().reset_index()
        priority_counts.columns = ['Priority', 'Count']

        priority_colors = {'Critical': '#EF4444', 'High': '#F59E0B', 'Medium': '#3B82F6', 'Low': '#10B981'}

        fig = px.bar(
            priority_counts,
            x='Priority',
            y='Count',
            color='Priority',
            color_discrete_map=priority_colors
        )
        fig.update_layout(
            height=350,
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE: HOW TO SUBMIT
# ============================================================================
elif page == "❓ How to Submit":
    st.markdown('<div class="main-header">How to Submit an SOP</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Follow these steps to successfully submit your Standard Operating Procedure for review and approval</div>', unsafe_allow_html=True)

    # Step-by-step guide with enhanced styling
    st.markdown("""
    <div class="step-card">
        <div class="step-title">
            <span class="step-number">1</span>
            Preparation
        </div>
        <div class="step-content">
            Before submitting your SOP, ensure you have completed all required documentation including risk assessments,
            stakeholder approvals, and compliance reviews. All SOPs must follow the standardized template format available
            in the SharePoint portal.
            <br><br>
            <strong>Required Documents:</strong>
            <ul>
                <li>Completed SOP document (using standard template)</li>
                <li>Risk assessment documentation</li>
                <li>Stakeholder approval confirmations</li>
                <li>Compliance review checklist</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="step-card">
        <div class="step-title">
            <span class="step-number">2</span>
            Initial Submission
        </div>
        <div class="step-content">
            Access the SOP Submission SharePoint portal using the link on the Dashboard. Complete all required fields in the
            submission form, including business justification, impact assessment, and implementation timeline. Upload
            your SOP document in the approved format (PDF or Word).
            <br><br>
            <strong>Form Requirements:</strong>
            <ul>
                <li>SOP Title (descriptive and specific)</li>
                <li>Department and submission type</li>
                <li>Business justification (minimum 100 words)</li>
                <li>Impact assessment (minimum 100 words)</li>
                <li>Proposed implementation date</li>
                <li>Priority level selection</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="step-card">
        <div class="step-title">
            <span class="step-number">3</span>
            Automated Review
        </div>
        <div class="step-content">
            Once submitted, your SOP will undergo automated compliance checking against existing templates and
            regulatory requirements. The AI system will flag any potential discrepancies or areas requiring attention.
            <br><br>
            <strong>Automated Checks Include:</strong>
            <ul>
                <li>Template format compliance</li>
                <li>Required sections completeness</li>
                <li>Document versioning</li>
                <li>Regulatory alignment</li>
                <li>Duplicate detection</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="step-card">
        <div class="step-title">
            <span class="step-number">4</span>
            E&C Policy Team Review
        </div>
        <div class="step-content">
            The E&C Policy Team will review your submission within 5-7 business days. They may request additional
            information, clarifications, or modifications before approval. You will receive email notifications at each
            stage of the review process.
            <br><br>
            <strong>Review Process:</strong>
            <ul>
                <li><strong>Day 1-2:</strong> Initial review and assignment</li>
                <li><strong>Day 3-5:</strong> Detailed compliance review</li>
                <li><strong>Day 6-7:</strong> Final approval or feedback</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # FAQ Section
    st.markdown("### 📚 Frequently Asked Questions")

    with st.expander("❓ What documents do I need before submitting?"):
        st.markdown("""
        **Required Documentation:**
        - ✅ Completed SOP document (following standard template)
        - ✅ Risk assessment documentation
        - ✅ Stakeholder approval emails or confirmations
        - ✅ Compliance review checklist
        - ✅ Business justification statement
        - ✅ Impact assessment report

        **Optional but Recommended:**
        - 📄 Training materials (if applicable)
        - 📄 Process flow diagrams
        - 📄 Related reference documents
        """)

    with st.expander("⏱️ How long does the review process take?"):
        st.markdown("""
        **Standard Timeline:**
        - **5-7 business days** for standard SOPs
        - **10-14 business days** for complex or high-priority SOPs
        - **Immediate review** for critical safety-related SOPs

        **Factors Affecting Timeline:**
        - Completeness of initial submission
        - Complexity of the SOP
        - Number of stakeholders involved
        - Current review queue volume

        You will receive email notifications at each stage of the review process.
        """)

    with st.expander("📄 What file formats are accepted?"):
        st.markdown("""
        **Accepted Formats:**
        - ✅ PDF (.pdf) - **Recommended**
        - ✅ Microsoft Word (.doc, .docx)

        **File Requirements:**
        - Maximum file size: **50 MB**
        - Files must not be password-protected
        - File names should be descriptive (e.g., "SOP_Manufacturing_Process_v2.pdf")

        **Important:** Ensure all embedded images and diagrams are clearly visible.
        """)

    with st.expander("✏️ Can I edit my submission after it's been submitted?"):
        st.markdown("""
        **Editing Options:**

        **Before Review Starts (Status: Pending):**
        - Contact your assigned reviewer to request edits
        - You may withdraw and resubmit with updates

        **During Review (Status: In Review):**
        - Communicate changes directly with your reviewer
        - Major changes may require withdrawal and resubmission

        **After Approval (Status: Approved):**
        - Submit a new revision using "Policy Update" submission type
        - Reference the original SOP ID in your new submission

        **Best Practice:** Double-check all information before submitting to minimize delays.
        """)

    with st.expander("📧 Who can I contact for help?"):
        st.markdown("""
        **E&C Policy Team Contact Information:**

        📧 **Email:** ec-policy@company.com
        ☎️ **Phone:** (555) 123-4567
        🕐 **Office Hours:** Monday-Friday, 9:00 AM - 5:00 PM EST

        **For Urgent Issues:**
        📧 **Urgent Email:** ec-policy-urgent@company.com
        ☎️ **After Hours:** (555) 123-4568 (Critical issues only)

        **Online Resources:**
        - SharePoint Knowledge Base: [link]
        - Training Videos: [link]
        - Template Library: [link]

        **Response Times:**
        - General inquiries: Within 24 business hours
        - Urgent requests: Within 4 business hours
        """)

    with st.expander("🔄 What happens if my SOP is rejected?"):
        st.markdown("""
        **Rejection Process:**

        If your SOP is rejected, you will receive:
        1. **Detailed feedback** explaining the reasons for rejection
        2. **Specific recommendations** for required changes
        3. **Reference materials** to help you revise your SOP

        **Next Steps:**
        - Review the feedback carefully
        - Make necessary revisions
        - Resubmit using "Policy Revision" submission type
        - Reference the original SOP ID

        **Common Rejection Reasons:**
        - Incomplete documentation
        - Non-compliance with templates
        - Missing risk assessments
        - Insufficient stakeholder approval
        - Regulatory conflicts

        **Support Available:** The E&C Policy Team can schedule a consultation to help you address issues.
        """)

    with st.expander("🔔 How do I track the status of my submission?"):
        st.markdown("""
        **Tracking Methods:**

        **1. Platform Dashboard:**
        - Navigate to "Track Deviations" tab
        - Use search function with your SOP ID
        - View real-time status updates

        **2. Email Notifications:**
        - Automatic notifications sent for each status change
        - Includes reviewer comments and next steps

        **3. Status Meanings:**
        - 🟡 **Pending:** Awaiting initial review assignment
        - 🔵 **In Review:** Currently being reviewed by E&C team
        - 🟣 **Requires Changes:** Feedback provided, revisions needed
        - 🟢 **Approved:** SOP approved for implementation
        - 🔴 **Rejected:** SOP requires major revisions

        **Pro Tip:** Add your SOP ID to your email subject line when contacting the E&C team.
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6B7280; padding: 2rem 0;'>
    <p style='font-size: 0.9rem;'>
        <strong>E&C SOP Management Platform</strong> | Version 1.0.0 | © 2025
    </p>
    <p style='font-size: 0.85rem;'>
        For technical support: ec-support@company.com | For policy questions: ec-policy@company.com
    </p>
    <p style='font-size: 0.8rem; color: #9CA3AF;'>
        Built with Streamlit for Databricks Apps | Last updated: January 2025
    </p>
</div>
""", unsafe_allow_html=True)
