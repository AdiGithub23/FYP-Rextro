import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId

load_dotenv()


class EmailNotificationService:
    def __init__(self):
        """
        Initialize SendGrid email service for sending alert notifications.
        Fetches recipient emails from MongoDB workspace members.
        """
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = "thisupun3@gmail.com"
        self.mongo_uri = os.getenv('MONGO_URI')
        
        if not self.api_key:
            print("⚠️ [EmailService] SENDGRID_API_KEY not found in environment variables")
            print("   Email notifications will be disabled")
            self.enabled = False
        else:
            self.enabled = True
            print(f"✅ [EmailService] Initialized with SendGrid API")
    
    def _get_workspace_user_emails(self, machine_id):
        """
        Fetch all user emails associated with the workspace matching machine_id.
        
        Args:
            machine_id (str): The machine/workspace ID
        
        Returns:
            list: List of email addresses
        """
        try:
            # Connect to MongoDB
            client = MongoClient(self.mongo_uri, server_api=ServerApi('1'))
            db = client["maintenancescheduler_db"]
            
            # Convert machine_id to ObjectId
            workspace_object_id = ObjectId(machine_id)
            
            # Find workspace
            workspace = db["workspaces"].find_one({"_id": workspace_object_id})
            
            if not workspace:
                print(f"⚠️ [EmailService] No workspace found for machine_id: {machine_id}")
                client.close()
                return []
            
            # Get all members
            members = workspace.get('members', [])
            email_list = []
            
            print(f"📧 [EmailService] Found {len(members)} members in workspace '{workspace.get('name', 'Unknown')}'")
            
            # Fetch user emails
            for member in members:
                user_id = member.get('user')
                role = member.get('role', 'Unknown')
                
                user = db["users"].find_one({"_id": user_id})
                
                if user and user.get('email'):
                    email = user.get('email')
                    name = user.get('name', 'Unknown')
                    email_list.append(email)
                    print(f"   • {name} ({role}): {email}")
            
            client.close()
            return email_list
            
        except Exception as e:
            print(f"❌ [EmailService] Error fetching workspace users: {str(e)}")
            return []
    
    def send_alert_email(self, alert_data, inference_count=None):
        """
        Send email notification to all workspace members based on alert status.
        
        Args:
            alert_data (dict): Alert information from inference service
                - status: 'normal' or 'critical'
                - message: Alert message
                - anomaly_scores: Dict of feature scores
                - critical_features: List of critical features
                - machine_id: Machine/workspace ID
            inference_count (int): Current inference number
        
        Returns:
            bool: True if all emails sent successfully, False otherwise
        """
        if not self.enabled:
            print("⚠️ [EmailService] Email notifications disabled (missing API key)")
            return False
        
        try:
            status = alert_data.get('status', 'unknown')
            message = alert_data.get('message', 'No message')
            anomaly_scores = alert_data.get('anomaly_scores', {})
            critical_features = alert_data.get('critical_features', [])
            timestamp = alert_data.get('timestamp', datetime.now().isoformat())
            machine_id = alert_data.get('machine_id', 'Unknown')
            
            # Get recipient emails from workspace
            recipient_emails = self._get_workspace_user_emails(machine_id)
            
            if not recipient_emails:
                print("⚠️ [EmailService] No recipient emails found. Skipping email notification.")
                return False
            
            # Determine email subject and content based on status
            if status == 'normal':
                subject = f"✅ Machine Status: Normal - Inference #{inference_count or 'N/A'}"
                email_body = self._generate_normal_email_body(
                    message, anomaly_scores, timestamp, inference_count, machine_id
                )
            elif status == 'critical':
                subject = f"🚨 CRITICAL ALERT: Machine At Risk - Inference #{inference_count or 'N/A'}"
                email_body = self._generate_critical_email_body(
                    message, anomaly_scores, critical_features, timestamp, inference_count, machine_id
                )
            else:
                subject = f"Machine Status Update - Inference #{inference_count or 'N/A'}"
                email_body = self._generate_generic_email_body(message, timestamp, inference_count)
            
            # Send email to all recipients
            sg = SendGridAPIClient(self.api_key)
            all_success = True
            
            print(f"\n📨 [EmailService] Sending emails to {len(recipient_emails)} recipients...")
            
            for recipient_email in recipient_emails:
                try:
                    message = Mail(
                        from_email=self.from_email,
                        to_emails=recipient_email,
                        subject=subject,
                        html_content=email_body
                    )
                    
                    response = sg.send(message)
                    
                    if response.status_code in [200, 201, 202]:
                        print(f"   ✅ Email sent to: {recipient_email}")
                    else:
                        print(f"   ⚠️ Unexpected status code for {recipient_email}: {response.status_code}")
                        all_success = False
                        
                except Exception as e:
                    print(f"   ❌ Failed to send email to {recipient_email}: {str(e)}")
                    all_success = False
            
            if all_success:
                print(f"✅ [EmailService] All emails sent successfully")
                print(f"   Subject: {subject}")
                print(f"   Recipients: {len(recipient_emails)}")
            else:
                print(f"⚠️ [EmailService] Some emails failed to send")
            
            return all_success
                
        except Exception as e:
            print(f"❌ [EmailService] Failed to send emails: {str(e)}")
            return False
    
    def _generate_normal_email_body(self, message, anomaly_scores, timestamp, inference_count, machine_id):
        """Generate HTML email body for normal status."""
        
        # Create anomaly scores table
        scores_rows = ""
        for feature, score in anomaly_scores.items():
            status_badge = "✅ Normal" if score < 30 else "⚠️ Warning"
            color = "#28a745" if score < 30 else "#ffc107"
            scores_rows += f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">{feature.upper()}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{score:.2f}%</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">
                    <span style="background: {color}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">
                        {status_badge}
                    </span>
                </td>
            </tr>
            """
        
        html_content = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 20px; text-align: center; border-radius: 8px; }}
                    .content {{ padding: 20px; background: #f8f9fa; border-radius: 8px; margin: 20px 0; }}
                    .table-container {{ margin: 20px 0; }}
                    table {{ width: 100%; border-collapse: collapse; background: white; }}
                    th {{ background: #28a745; color: white; padding: 10px; text-align: left; }}
                    .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>✅ Machine Condition: Normal</h1>
                    <p>Inference #{inference_count or 'N/A'}</p>
                </div>
                
                <div class="content">
                    <h2>Status Update</h2>
                    <p><strong>Machine ID:</strong> {machine_id}</p>
                    <p><strong>Message:</strong> {message}</p>
                    <p><strong>Timestamp:</strong> {datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')}</p>
                    
                    <div class="table-container">
                        <h3>Anomaly Scores by Feature</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>Feature</th>
                                    <th style="text-align: center;">Anomaly Score</th>
                                    <th style="text-align: center;">Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {scores_rows}
                            </tbody>
                        </table>
                    </div>
                    
                    <p style="color: #28a745; font-weight: bold; margin-top: 20px;">
                        ✅ All systems operating normally. No action required.
                    </p>
                </div>
                
                <div class="footer">
                    <p>This is an automated notification from the Machine Condition Monitoring System</p>
                    <p>Powered by PatchTST Forecasting Model</p>
                </div>
            </body>
        </html>
        """
        return html_content
    
    def _generate_critical_email_body(self, message, anomaly_scores, critical_features, timestamp, inference_count, machine_id):
        """Generate HTML email body for critical status."""
        
        # Create anomaly scores table with highlighting for critical features
        scores_rows = ""
        for feature, score in anomaly_scores.items():
            is_critical = feature in critical_features
            if is_critical:
                status_badge = "🚨 CRITICAL"
                color = "#dc3545"
                row_style = "background: #f8d7da;"
            elif score >= 15:
                status_badge = "⚠️ Warning"
                color = "#ffc107"
                row_style = ""
            else:
                status_badge = "✅ Normal"
                color = "#28a745"
                row_style = ""
            
            scores_rows += f"""
            <tr style="{row_style}">
                <td style="padding: 8px; border: 1px solid #ddd;">
                    {feature.upper()} {'🔴' if is_critical else ''}
                </td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center; font-weight: bold;">{score:.2f}%</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">
                    <span style="background: {color}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">
                        {status_badge}
                    </span>
                </td>
            </tr>
            """
        
        # Create critical features list
        critical_list = ""
        for feature in critical_features:
            score = anomaly_scores.get(feature, 0)
            critical_list += f"<li><strong>{feature.upper()}</strong>: {score:.2f}% anomaly rate</li>"
        
        html_content = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background: linear-gradient(135deg, #dc3545, #c82333); color: white; padding: 20px; text-align: center; border-radius: 8px; }}
                    .content {{ padding: 20px; background: #f8f9fa; border-radius: 8px; margin: 20px 0; }}
                    .alert-box {{ background: #f8d7da; border: 2px solid #dc3545; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                    .table-container {{ margin: 20px 0; }}
                    table {{ width: 100%; border-collapse: collapse; background: white; }}
                    th {{ background: #dc3545; color: white; padding: 10px; text-align: left; }}
                    .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🚨 CRITICAL ALERT: Machine At Risk</h1>
                    <p>Inference #{inference_count or 'N/A'}</p>
                </div>
                
                <div class="content">
                    <div class="alert-box">
                        <h2 style="color: #dc3545; margin: 0;">⚠️ Immediate Attention Required</h2>
                        <p style="margin: 10px 0;"><strong>Machine ID:</strong> {machine_id}</p>
                        <p style="margin: 10px 0;"><strong>Message:</strong> {message}</p>
                        <p style="margin: 10px 0;"><strong>Timestamp:</strong> {datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    
                    <h3>🎯 Critical Features Detected:</h3>
                    <ul style="color: #dc3545; font-weight: bold;">
                        {critical_list}
                    </ul>
                    
                    <div class="table-container">
                        <h3>Anomaly Scores by Feature</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>Feature</th>
                                    <th style="text-align: center;">Anomaly Score</th>
                                    <th style="text-align: center;">Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {scores_rows}
                            </tbody>
                        </table>
                        <p style="font-size: 12px; color: #666; margin-top: 10px;">
                            🔴 = Critical feature (≥30% anomaly threshold exceeded)
                        </p>
                    </div>
                    
                    <p style="color: #dc3545; font-weight: bold; margin-top: 20px;">
                        ⚠️ ACTION REQUIRED: Inspect the highlighted sensors and perform necessary maintenance.
                    </p>
                </div>
                
                <div class="footer">
                    <p>This is an automated critical alert from the Machine Condition Monitoring System</p>
                    <p>Powered by PatchTST Forecasting Model</p>
                </div>
            </body>
        </html>
        """
        return html_content
    
    def _generate_generic_email_body(self, message, timestamp, inference_count):
        """Generate HTML email body for generic status."""
        html_content = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background: linear-gradient(135deg, #17a2b8, #138496); color: white; padding: 20px; text-align: center; border-radius: 8px; }}
                    .content {{ padding: 20px; background: #f8f9fa; border-radius: 8px; margin: 20px 0; }}
                    .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Machine Status Update</h1>
                    <p>Inference #{inference_count or 'N/A'}</p>
                </div>
                
                <div class="content">
                    <p><strong>Message:</strong> {message}</p>
                    <p><strong>Timestamp:</strong> {datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="footer">
                    <p>This is an automated notification from the Machine Condition Monitoring System</p>
                    <p>Powered by PatchTST Forecasting Model</p>
                </div>
            </body>
        </html>
        """
        return html_content