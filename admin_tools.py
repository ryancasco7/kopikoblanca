import streamlit as st
import pandas as pd
from activity_log import get_recent_activities, log_activity, get_activities_by_type
from datetime import datetime


def show_admin_tools(df):
    st.markdown("## ⚙️ Administrative Tools")
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Data Management", "Export Visualizations", "Data Statistics", "Recent Activities"])
    
    with tab1:
        st.subheader("Dataset Information")
        st.write(f"**Total Records:** {len(df)}")
        st.write(f"**Total Features:** {len(df.columns)}")
        st.write(f"**Clusters:** {df['Cluster'].nunique()}")
        
        st.divider()
        
        st.subheader("Preview Data")
        num_rows = st.number_input("Number of rows to display", min_value=1, max_value=100, value=10, key="admin_rows")
        st.dataframe(df.head(num_rows), use_container_width=True)
        
        st.subheader("Download Data")
        csv = df.to_csv(index=False).encode('utf-8')
        username = st.session_state.get('username', 'Unknown')
        
        # Initialize session state for download preparation
        if 'download_prepared' not in st.session_state:
            st.session_state.download_prepared = False
        
        # Create a wrapper button to log and then trigger download
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("📥 Prepare Download", key="prepare_download_btn"):
                # Log download activity
                log_activity(
                    activity_type='download',
                    user=username,
                    description=f"Initiated download of clustering results as CSV",
                    details={'file_type': 'CSV', 'records': len(df)}
                )
                st.session_state.download_prepared = True
                st.success("✅ Download prepared! Click the download button below.")
                st.rerun()
        
        # Show download button
        if st.session_state.get('download_prepared', False):
            st.download_button(
                label="⬇️ Download CSV File",
                data=csv,
                file_name="clustering_results.csv",
                mime="text/csv",
                key="download_main_csv"
            )
            if st.button("Cancel", key="cancel_download"):
                st.session_state.download_prepared = False
                st.rerun()
        else:
            st.info("💡 Click 'Prepare Download' to log the activity and enable download.")
    
    with tab2:
        st.subheader("Export Visualizations")
        
        export_format = st.selectbox("Export Format", ["PNG", "PDF", "HTML"], key="export_format_select")
        username = st.session_state.get('username', 'Unknown')
        
        if st.button("Generate All Visualizations", key="generate_viz_btn"):
            # Log export activity
            log_activity(
                activity_type='export',
                user=username,
                description=f"Attempted to export visualizations in {export_format} format",
                details={'format': export_format, 'status': 'feature_in_progress'}
            )
            st.info("📊 Visualization export feature - implementation in progress")
            st.write("This feature will allow you to export:")
            st.write("- Cluster distribution charts")
            st.write("- PCA visualizations")
            st.write("- Domain comparison graphs")
            st.write("- Training needs heatmaps")
            st.success("✅ Export request logged in activity history.")
    
    with tab3:
        st.subheader("Detailed Statistics")
        
        st.write("**Cluster Distribution:**")
        cluster_stats = pd.DataFrame({
            'Cluster': df['Cluster'].value_counts().sort_index(),
            'Percentage': (df['Cluster'].value_counts(normalize=True).sort_index() * 100).round(2)
        })
        st.dataframe(cluster_stats, use_container_width=True)
        
        st.divider()
        
        st.write("**Missing Values Check:**")
        missing = df.isnull().sum()
        if missing.sum() > 0:
            st.dataframe(missing[missing > 0], use_container_width=True)
        else:
            st.success("✅ No missing values in the dataset!")
        
        st.divider()
        
        st.write("**Competency Ratings Summary:**")
        competency_cols = [col for col in df.columns if col.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.', '11.', '12.', '13.'))]
        if competency_cols:
            comp_stats = df[competency_cols].describe().round(2)
            st.dataframe(comp_stats, use_container_width=True)
    
    with tab4:
        st.subheader("📋 Recent Activities")
        st.markdown("View recent system activities and user actions.")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            activity_limit = st.number_input("Number of activities to show", min_value=10, max_value=100, value=30, step=5)
        with col2:
            activity_filter = st.selectbox("Filter by type", ["All", "login", "logout", "download", "assessment", "export"])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Activity type icons and colors (define outside conditional blocks)
        activity_icons = {
            'login': '🔓',
            'logout': '🔒',
            'download': '📥',
            'assessment': '📝',
            'export': '📊',
            'signup': '➕',
            'admin_action': '⚙️'
        }
        
        activity_colors = {
            'login': '#4CAF50',
            'logout': '#F44336',
            'download': '#2196F3',
            'assessment': '#FF9800',
            'export': '#9C27B0',
            'signup': '#00BCD4',
            'admin_action': '#607D8B'
        }
        
        # Get activities
        if activity_filter == "All":
            activities = get_recent_activities(limit=activity_limit)
        else:
            activities = get_activities_by_type(activity_filter, limit=activity_limit)
        
        if activities:
            
            # Display activities
            st.markdown("""
                <style>
                .activity-item {
                    background: white;
                    padding: 1rem;
                    border-radius: 8px;
                    margin-bottom: 0.75rem;
                    border-left: 4px solid;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }
                .activity-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 0.5rem;
                }
                .activity-type {
                    font-weight: 600;
                    font-size: 0.95rem;
                }
                .activity-timestamp {
                    color: #666;
                    font-size: 0.85rem;
                }
                .activity-user {
                    color: #1E88E5;
                    font-weight: 500;
                    font-size: 0.9rem;
                }
                .activity-description {
                    color: #333;
                    margin-top: 0.5rem;
                }
                </style>
            """, unsafe_allow_html=True)
            
            for activity in activities:
                activity_type = activity.get('type', 'unknown')
                icon = activity_icons.get(activity_type, '📌')
                color = activity_colors.get(activity_type, '#757575')
                user = activity.get('user', 'Unknown')
                description = activity.get('description', 'No description')
                timestamp = activity.get('timestamp', 'Unknown time')
                details = activity.get('details', {})
                
                # Build details string
                details_str = ""
                if details:
                    detail_parts = []
                    for key, value in details.items():
                        detail_parts.append(f"{key}: {value}")
                    if detail_parts:
                        details_str = " | " + " | ".join(detail_parts)
                
                st.markdown(f'''
                    <div class="activity-item" style="border-left-color: {color};">
                        <div class="activity-header">
                            <div>
                                <span class="activity-type">{icon} {activity_type.upper()}</span>
                                <span class="activity-user"> by {user}</span>
                            </div>
                            <span class="activity-timestamp">{timestamp}</span>
                        </div>
                        <div class="activity-description">
                            {description}{details_str}
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("📭 No activities found. Activities will appear here as users interact with the system.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Activity statistics
        st.subheader("📊 Activity Statistics")
        all_activities = get_recent_activities(limit=1000)
        
        if all_activities:
            # Count by type
            activity_counts = {}
            for activity in all_activities:
                activity_type = activity.get('type', 'unknown')
                activity_counts[activity_type] = activity_counts.get(activity_type, 0) + 1
            
            # Count by user
            user_counts = {}
            for activity in all_activities:
                user = activity.get('user', 'Unknown')
                user_counts[user] = user_counts.get(user, 0) + 1
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Activities by Type**")
                for activity_type, count in sorted(activity_counts.items(), key=lambda x: x[1], reverse=True):
                    icon = activity_icons.get(activity_type, '📌')
                    st.write(f"{icon} {activity_type.title()}: **{count}**")
            
            with col2:
                st.markdown("**Activities by User**")
                for user, count in sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                    st.write(f"👤 {user}: **{count}**")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.info(f"📈 Total activities logged: **{len(all_activities)}**")
        else:
            st.info("No activity statistics available yet.")

