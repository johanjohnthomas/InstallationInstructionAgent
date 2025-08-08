import os
import json
from typing import List, Dict, Any, Optional
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class GoogleSheetsManager:
    def __init__(self):
        self.sheets_id = os.getenv("GOOGLE_SHEETS_ID")
        self.service_account_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        
        if not self.sheets_id:
            raise ValueError("GOOGLE_SHEETS_ID not found in environment variables")
        
        # For now, we'll use a fallback method if service account isn't available
        self.client = None
        self.worksheet = None
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize Google Sheets client with authentication"""
        try:
            if self.service_account_path and os.path.exists(self.service_account_path):
                # Use service account authentication
                scope = ['https://spreadsheets.google.com/feeds', 
                        'https://www.googleapis.com/auth/drive']
                credentials = Credentials.from_service_account_file(
                    self.service_account_path, scopes=scope)
                self.client = gspread.authorize(credentials)
            else:
                # For development, we'll work with local CSV data
                print("Warning: Service account not found. Working in development mode with CSV data.")
                return
                
            # Open the Google Sheet
            self.sheet = self.client.open_by_key(self.sheets_id)
            self.worksheet = self.sheet.sheet1  # Assuming first worksheet
            
        except Exception as e:
            print(f"Warning: Could not connect to Google Sheets: {e}")
            print("Working in development mode with local CSV data.")
    
    def read_sheet_data(self) -> List[Dict]:
        """
        Read all data from the Google Sheet and return as list of dictionaries
        """
        try:
            if self.worksheet:
                # Get all records from Google Sheets
                records = self.worksheet.get_all_records()
                return records
            else:
                # Fallback: read from local CSV
                return self._read_local_csv()
        except Exception as e:
            print(f"Error reading sheet data: {e}")
            return self._read_local_csv()
    
    def _read_local_csv(self) -> List[Dict]:
        """Fallback method to read local CSV data"""
        try:
            csv_path = "Copy of internshipjourney - Sheet1.csv"
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                # Clean up the data
                df = df.fillna('')  # Replace NaN with empty strings
                return df.to_dict('records')
            else:
                return []
        except Exception as e:
            print(f"Error reading local CSV: {e}")
            return []
    
    def write_changes_to_sheet(self, changes: List[Dict], existing_data: List[Dict]) -> bool:
        """
        Apply the changes to the Google Sheet
        
        Args:
            changes: List of change dictionaries from SheetsAgent
            existing_data: Current sheet data
            
        Returns:
            bool: Success status
        """
        try:
            if not self.worksheet:
                print("Google Sheets not available. Changes would be applied to:")
                self._preview_csv_changes(changes, existing_data)
                return True
            
            for change in changes:
                action = change.get('action')
                data = change.get('data', {})
                
                if action == 'update' and change.get('row_id'):
                    # Update existing row (row_id is 1-based, add 1 for header)
                    row_num = int(change['row_id']) + 1
                    self._update_row(row_num, data)
                    
                elif action == 'create':
                    # Add new row
                    self._add_new_row(data)
            
            return True
            
        except Exception as e:
            print(f"Error writing to sheet: {e}")
            return False
    
    def _update_row(self, row_num: int, data: Dict):
        """Update a specific row in the sheet"""
        try:
            # Get headers to know column positions
            headers = self.worksheet.row_values(1)
            
            # Update each field
            for field, value in data.items():
                if field in headers:
                    col_num = headers.index(field) + 1
                    self.worksheet.update_cell(row_num, col_num, str(value))
                    
        except Exception as e:
            print(f"Error updating row {row_num}: {e}")
    
    def _add_new_row(self, data: Dict):
        """Add a new row to the sheet"""
        try:
            # Get headers
            headers = self.worksheet.row_values(1)
            
            # Create row data in correct order
            row_data = []
            for header in headers:
                row_data.append(str(data.get(header, '')))
            
            # Append the row
            self.worksheet.append_row(row_data)
            
        except Exception as e:
            print(f"Error adding new row: {e}")
    
    def _preview_csv_changes(self, changes: List[Dict], existing_data: List[Dict]):
        """Preview what changes would be made to CSV (development mode)"""
        print("\n=== DEVELOPMENT MODE: CSV CHANGES PREVIEW ===")
        
        for change in changes:
            action = change.get('action')
            data = change.get('data', {})
            
            print(f"\nAction: {action.upper()}")
            if action == 'update' and change.get('row_id'):
                print(f"Would update row {change['row_id']}:")
            else:
                print("Would add new row:")
            
            for key, value in data.items():
                print(f"  {key}: {value}")
    
    def backup_sheet_data(self) -> str:
        """Create a backup of current sheet data"""
        try:
            data = self.read_sheet_data()
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"backup_sheet_{timestamp}.json"
            
            with open(backup_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return backup_file
            
        except Exception as e:
            print(f"Error creating backup: {e}")
            return ""
    
    def get_sheet_info(self) -> Dict:
        """Get information about the current sheet"""
        try:
            data = self.read_sheet_data()
            
            info = {
                'total_rows': len(data),
                'workstreams': list(set([row.get('Workstream', '') for row in data if row.get('Workstream')])),
                'statuses': list(set([row.get('Status', '') for row in data if row.get('Status')])),
                'last_updated': pd.Timestamp.now().isoformat()
            }
            
            return info
            
        except Exception as e:
            print(f"Error getting sheet info: {e}")
            return {}
    
    def validate_sheet_structure(self) -> bool:
        """Validate that the sheet has the expected columns"""
        expected_columns = [
            'Workstream', 'Task', 'Sub Task', 'Start Date', 
            'End Date', 'Effort', 'Status', 'Priority', 'Tags'
        ]
        
        try:
            if self.worksheet:
                headers = self.worksheet.row_values(1)
            else:
                # Check local CSV
                csv_path = "Copy of internshipjourney - Sheet1.csv"
                if os.path.exists(csv_path):
                    df = pd.read_csv(csv_path)
                    headers = df.columns.tolist()
                else:
                    return False
            
            # Check if all expected columns exist
            missing_columns = []
            for col in expected_columns:
                if col not in headers:
                    missing_columns.append(col)
            
            if missing_columns:
                print(f"Warning: Missing columns in sheet: {missing_columns}")
                return False
            
            return True
            
        except Exception as e:
            print(f"Error validating sheet structure: {e}")
            return False
    
    def get_development_mode_status(self) -> bool:
        """Check if we're running in development mode (without Google Sheets access)"""
        return self.worksheet is None