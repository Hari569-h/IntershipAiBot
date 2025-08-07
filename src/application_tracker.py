import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd

class ApplicationTracker:
    def __init__(self, applications_file: str = "applications.txt"):
        """Initialize application tracker with text file storage."""
        self.applications_file = applications_file
        self.applications = self.load_applications()
        
    def load_applications(self) -> List[Dict]:
        """Load applications from text file."""
        try:
            if os.path.exists(self.applications_file):
                with open(self.applications_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        return json.loads(content)
            return []
        except Exception as e:
            print(f"❌ Error loading applications: {e}")
            return []
    
    def save_applications(self):
        """Save applications to text file."""
        try:
            with open(self.applications_file, 'w', encoding='utf-8') as f:
                json.dump(self.applications, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error saving applications: {e}")
    
    def add_application(self, title: str, company: str, platform: str, 
                       link: str = "", similarity_score: float = 0.0, 
                       status: str = "Applied", applied_at: str = None) -> bool:
        """Add a new application to the tracker."""
        try:
            if applied_at is None:
                applied_at = datetime.now().isoformat()
            
            application = {
                'id': len(self.applications) + 1,
                'title': title,
                'company': company,
                'platform': platform,
                'link': link,
                'similarity_score': similarity_score,
                'status': status,
                'applied_at': applied_at,
                'tracked_at': datetime.now().isoformat()
            }
            
            self.applications.append(application)
            self.save_applications()
            
            print(f"✅ Application tracked: {title} at {company} ({status})")
            return True
            
        except Exception as e:
            print(f"❌ Error adding application: {e}")
            return False
    
    def update_application_status(self, application_id: int, new_status: str) -> bool:
        """Update the status of an application."""
        try:
            for app in self.applications:
                if app['id'] == application_id:
                    app['status'] = new_status
                    app['updated_at'] = datetime.now().isoformat()
                    self.save_applications()
                    print(f"✅ Updated application {application_id} status to: {new_status}")
                    return True
            
            print(f"❌ Application {application_id} not found")
            return False
            
        except Exception as e:
            print(f"❌ Error updating application: {e}")
            return False
    
    def get_applications(self, status: str = None, platform: str = None) -> List[Dict]:
        """Get applications with optional filtering."""
        filtered_applications = self.applications
        
        if status:
            filtered_applications = [app for app in filtered_applications if app['status'] == status]
        
        if platform:
            filtered_applications = [app for app in filtered_applications if app['platform'] == platform]
        
        return filtered_applications
    
    def get_applications_summary(self) -> Dict:
        """Get summary statistics of applications."""
        if not self.applications:
            return {
                'total_applications': 0,
                'successful_applications': 0,
                'failed_applications': 0,
                'pending_applications': 0,
                'platforms': {},
                'recent_applications': []
            }
        
        total = len(self.applications)
        successful = len([app for app in self.applications if app['status'] == 'Applied'])
        failed = len([app for app in self.applications if app['status'] == 'Failed'])
        pending = len([app for app in self.applications if app['status'] == 'Pending'])
        
        # Count by platform
        platforms = {}
        for app in self.applications:
            platform = app['platform']
            platforms[platform] = platforms.get(platform, 0) + 1
        
        # Get recent applications (last 10)
        recent = sorted(self.applications, key=lambda x: x['applied_at'], reverse=True)[:10]
        
        return {
            'total_applications': total,
            'successful_applications': successful,
            'failed_applications': failed,
            'pending_applications': pending,
            'platforms': platforms,
            'recent_applications': recent
        }
    
    def export_to_csv(self, filename: str = "applications_export.csv") -> bool:
        """Export applications to CSV file."""
        try:
            if not self.applications:
                print("⚠️ No applications to export")
                return False
            
            df = pd.DataFrame(self.applications)
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"✅ Exported {len(self.applications)} applications to {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
            return False
    
    def export_to_excel(self, filename: str = "applications_export.xlsx") -> bool:
        """Export applications to Excel file."""
        try:
            if not self.applications:
                print("⚠️ No applications to export")
                return False
            
            df = pd.DataFrame(self.applications)
            df.to_excel(filename, index=False, engine='openpyxl')
            print(f"✅ Exported {len(self.applications)} applications to {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting to Excel: {e}")
            return False
    
    def clear_applications(self) -> bool:
        """Clear all applications (use with caution)."""
        try:
            self.applications = []
            self.save_applications()
            print("✅ All applications cleared")
            return True
        except Exception as e:
            print(f"❌ Error clearing applications: {e}")
            return False
    
    def get_application_by_id(self, application_id: int) -> Optional[Dict]:
        """Get a specific application by ID."""
        for app in self.applications:
            if app['id'] == application_id:
                return app
        return None
    
    def search_applications(self, query: str) -> List[Dict]:
        """Search applications by title or company name."""
        query = query.lower()
        results = []
        
        for app in self.applications:
            if (query in app['title'].lower() or 
                query in app['company'].lower()):
                results.append(app)
        
        return results 