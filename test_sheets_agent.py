#!/usr/bin/env python3
"""
Test script for the Google Sheets Agent functionality
"""

import os
import json
from dotenv import load_dotenv
from sheets_agent import SheetsAgent
from sheets_tools import GoogleSheetsManager

load_dotenv()

def test_basic_functionality():
    """Test basic agent functionality with sample data"""
    print("🧪 Testing Google Sheets Agent...")
    
    # Test sample daily updates
    sample_updates = [
        "Today I completed the user authentication module and started working on the database integration",
        "Spent the morning debugging the API endpoints and finished the unit tests for the auth system",
        "Working on the BigQuery ML model for stock prediction, currently experimenting with different algorithms",
        "Attended the team meeting and reviewed the health check reports, planning to define questions for the analytics team next week"
    ]
    
    try:
        # Initialize components
        print("Initializing Google Sheets Manager...")
        sheets_manager = GoogleSheetsManager()
        
        print("Initializing Sheets Agent...")
        agent = SheetsAgent()
        
        # Load sample sheet data
        print("Loading sheet data...")
        sheet_data = sheets_manager.read_sheet_data()
        print(f"Loaded {len(sheet_data)} existing rows from sheet")
        
        # Test each sample update
        for i, update_text in enumerate(sample_updates, 1):
            print(f"\n--- Test Case {i} ---")
            print(f"Update: {update_text}")
            
            try:
                # Parse the updates
                changes = agent.parse_daily_updates(update_text, sheet_data)
                
                if changes:
                    # Validate changes
                    validated_changes = agent.validate_changes(changes, sheet_data)
                    
                    # Generate preview
                    preview = agent.preview_changes(validated_changes, sheet_data)
                    
                    print(f"Generated {len(validated_changes)} changes:")
                    for j, change in enumerate(validated_changes, 1):
                        action = change.get('action', 'unknown')
                        task = change.get('data', {}).get('Task', 'N/A')
                        status = change.get('data', {}).get('Status', 'N/A')
                        print(f"  {j}. {action.upper()}: {task} ({status})")
                    
                    print("\nPreview:")
                    print(preview)
                    
                else:
                    print("No changes identified for this update")
                    
            except Exception as e:
                print(f"❌ Error processing update: {e}")
                
        print("\n✅ Basic functionality test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

def test_sheet_validation():
    """Test sheet structure validation"""
    print("\n🔍 Testing sheet validation...")
    
    try:
        sheets_manager = GoogleSheetsManager()
        
        is_valid = sheets_manager.validate_sheet_structure()
        if is_valid:
            print("✅ Sheet structure is valid")
        else:
            print("⚠️ Sheet structure validation failed")
            
        # Show development mode status
        dev_mode = sheets_manager.get_development_mode_status()
        if dev_mode:
            print("🔧 Running in development mode (local CSV)")
        else:
            print("🌐 Connected to Google Sheets")
            
    except Exception as e:
        print(f"❌ Validation test failed: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting Google Sheets Agent Tests\n")
    
    # Check environment setup
    print("Checking environment...")
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if google_api_key:
        print("✅ Google API key found")
    else:
        print("❌ Google API key missing")
        return
    
    # Run tests
    test_sheet_validation()
    test_basic_functionality()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main()