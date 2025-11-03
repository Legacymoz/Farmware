#!/usr/bin/env python3
"""
Database Management Script for Farmware
Provides individual functions to manage database tables and data.
Can be run with different commands to perform specific operations.
"""

import os
import sys
import argparse
from datetime import datetime

# Add the parent directory to Python path so we can import ServerLogic
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ServerLogic import create_app, db
from ServerLogic.models import Farmer, Advisory, FarmingAdvisory

def get_app_context():
    """Get Flask app context"""
    app = create_app()
    return app.app_context()

def clear_database():
    """Clear all data from all tables"""
    print("🗑️  Clearing entire database...")
    try:
        with get_app_context():
            # Delete in reverse order of dependencies
            deleted_fa = FarmingAdvisory.query.count()
            deleted_advisories = Advisory.query.count()
            deleted_farmers = Farmer.query.count()
            
            FarmingAdvisory.query.delete()
            Advisory.query.delete()
            Farmer.query.delete()
            db.session.commit()
            
            print(f"✅ Database cleared successfully!")
            print(f"   - Deleted {deleted_fa} farming advisory records")
            print(f"   - Deleted {deleted_advisories} advisories") 
            print(f"   - Deleted {deleted_farmers} farmers")
            
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        with get_app_context():
            db.session.rollback()
        raise

def clear_farmers_table():
    """Clear only the farmers table (and related farming advisories)"""
    print("🗑️  Clearing farmers table...")
    try:
        with get_app_context():
            # First delete farming advisories that reference farmers
            deleted_fa = FarmingAdvisory.query.count()
            deleted_farmers = Farmer.query.count()
            
            FarmingAdvisory.query.delete()
            Farmer.query.delete()
            db.session.commit()
            
            print(f"✅ Farmers table cleared successfully!")
            print(f"   - Deleted {deleted_fa} farming advisory records") 
            print(f"   - Deleted {deleted_farmers} farmers")
            
    except Exception as e:
        print(f"❌ Error clearing farmers table: {e}")
        with get_app_context():
            db.session.rollback()
        raise

def clear_advisory_table():
    """Clear only the advisory table (and related farming advisories)"""
    print("🗑️  Clearing advisory table...")
    try:
        with get_app_context():
            # First delete farming advisories that reference advisories
            deleted_fa = FarmingAdvisory.query.count()
            deleted_advisories = Advisory.query.count()
            
            FarmingAdvisory.query.delete()
            Advisory.query.delete()
            db.session.commit()
            
            print(f"✅ Advisory table cleared successfully!")
            print(f"   - Deleted {deleted_fa} farming advisory records")
            print(f"   - Deleted {deleted_advisories} advisories")
            
    except Exception as e:
        print(f"❌ Error clearing advisory table: {e}")
        with get_app_context():
            db.session.rollback()
        raise

def create_farmer(phone, secret_key_text):
    """Create a single farmer"""
    print(f"👨‍🌾 Creating farmer with phone: {phone}")
    try:
        with get_app_context():
            # Convert secret key text to bytes
            secret_key_bytes = secret_key_text.encode('utf-8')
            
            farmer = Farmer(
                phone=phone,
                secret_key=secret_key_bytes
            )
            
            db.session.add(farmer)
            db.session.commit()
            
            print(f"✅ Farmer created successfully!")
            print(f"   - ID: {farmer.id}")
            print(f"   - Phone: {farmer.phone}")
            print(f"   - Secret Key: {secret_key_text}")
            
            return farmer
            
    except Exception as e:
        print(f"❌ Error creating farmer: {e}")
        with get_app_context():
            db.session.rollback()
        raise

def create_advisory(title, message):
    """Create a single advisory"""
    print(f"📢 Creating advisory: {title}")
    try:
        with get_app_context():
            advisory = Advisory(
                title=title,
                message=message
            )
            
            db.session.add(advisory)
            db.session.commit()
            
            print(f"✅ Advisory created successfully!")
            print(f"   - ID: {advisory.id}")
            print(f"   - Title: {advisory.title}")
            print(f"   - Message: {advisory.message[:50]}...")
            
            return advisory
            
    except Exception as e:
        print(f"❌ Error creating advisory: {e}")
        with get_app_context():
            db.session.rollback()
        raise

def delete_farmer(farmer_id):
    """Delete a specific farmer by ID"""
    print(f"🗑️  Deleting farmer with ID: {farmer_id}")
    try:
        with get_app_context():
            # Find the farmer
            farmer = Farmer.query.get(farmer_id)
            if not farmer:
                print(f"❌ Farmer with ID {farmer_id} not found")
                return
            
            # Count related farming advisories that will be deleted
            related_fa = FarmingAdvisory.query.filter_by(farmer_id=farmer_id).count()
            
            # Delete related farming advisories first
            FarmingAdvisory.query.filter_by(farmer_id=farmer_id).delete()
            
            # Store farmer info for confirmation message
            farmer_phone = farmer.phone
            
            # Delete the farmer
            db.session.delete(farmer)
            db.session.commit()
            
            print(f"✅ Farmer deleted successfully!")
            print(f"   - ID: {farmer_id}")
            print(f"   - Phone: {farmer_phone}")
            print(f"   - Also deleted {related_fa} related farming advisory records")
            
    except Exception as e:
        print(f"❌ Error deleting farmer: {e}")
        with get_app_context():
            db.session.rollback()
        raise

def delete_advisory(advisory_id):
    """Delete a specific advisory by ID"""
    print(f"🗑️  Deleting advisory with ID: {advisory_id}")
    try:
        with get_app_context():
            # Find the advisory
            advisory = Advisory.query.get(advisory_id)
            if not advisory:
                print(f"❌ Advisory with ID {advisory_id} not found")
                return
            
            # Count related farming advisories that will be deleted
            related_fa = FarmingAdvisory.query.filter_by(advisory_id=advisory_id).count()
            
            # Delete related farming advisories first
            FarmingAdvisory.query.filter_by(advisory_id=advisory_id).delete()
            
            # Store advisory info for confirmation message
            advisory_title = advisory.title
            
            # Delete the advisory
            db.session.delete(advisory)
            db.session.commit()
            
            print(f"✅ Advisory deleted successfully!")
            print(f"   - ID: {advisory_id}")
            print(f"   - Title: {advisory_title}")
            print(f"   - Also deleted {related_fa} related farming advisory records")
            
    except Exception as e:
        print(f"❌ Error deleting advisory: {e}")
        with get_app_context():
            db.session.rollback()
        raise

def create_sample_farmers():
    """Create sample farmers for testing"""
    print("👨‍🌾 Creating sample farmers...")
    
    farmers_data = [
        ('+254798929952', 'FarmwareSecret2025'),
        ('+254759216739', 'AnotherAwesomeKey1'),
        ('+254110726703', 'ThirdFarmerKey456'),
    ]
    
    created_farmers = []
    for phone, secret_key in farmers_data:
        farmer = create_farmer(phone, secret_key)
        created_farmers.append(farmer)
    
    print(f"✅ Created {len(created_farmers)} sample farmers")
    return created_farmers

def create_sample_advisories():
    """Create sample advisories for testing"""
    print("📢 Creating sample advisories...")
    
    advisories_data = [
        (
            'Weather Alert: Heavy Rain Expected',
            'Heavy rain is expected in your area today. Please take necessary precautions to protect your crops and livestock. Secure any outdoor equipment and ensure proper drainage in your fields.'
        ),
        (
            'Pest Control Advisory',
            'Recent reports indicate increased pest activity in the region. Inspect your crops regularly for signs of pest damage. Apply appropriate pest control measures as recommended.'
        ),
        (
            'Market Price Update',
            'Current market prices: Maize - KES 45/kg, Beans - KES 120/kg, Tomatoes - KES 80/kg. Consider timing your harvest and sales to maximize profits.'
        ),
        (
            'Fertilizer Application Reminder',
            'This is the optimal time for fertilizer application in your area. Use recommended NPK ratios for your specific crops. Apply during cool hours to prevent plant burn.'
        ),
    ]
    
    created_advisories = []
    for title, message in advisories_data:
        advisory = create_advisory(title, message)
        created_advisories.append(advisory)
    
    print(f"✅ Created {len(created_advisories)} sample advisories")
    return created_advisories

def show_status():
    """Show current database status (counts and basic info)"""
    print("📊 Current Database Status:")
    try:
        with get_app_context():
            farmer_count = Farmer.query.count()
            advisory_count = Advisory.query.count()
            fa_count = FarmingAdvisory.query.count()
            
            print(f"   👨‍🌾 Farmers: {farmer_count}")
            print(f"   📢 Advisories: {advisory_count}")
            print(f"   📱 Farming Advisory Records: {fa_count}")
            
            if farmer_count > 0:
                print("\n👨‍🌾 Farmers:")
                for farmer in Farmer.query.all():
                    print(f"   ID: {farmer.id:2d} | Phone: {farmer.phone}")
            
            if advisory_count > 0:
                print("\n📢 Advisories:")
                for advisory in Advisory.query.all():
                    title = advisory.title[:40] + "..." if len(advisory.title) > 40 else advisory.title
                    print(f"   ID: {advisory.id:2d} | Title: {title}")
                    
    except Exception as e:
        print(f"❌ Error getting database status: {e}")

def show_all_data():
    """Show all data from all tables with full details"""
    print("📚 Complete Database Contents:")
    try:
        with get_app_context():
            # Show Farmers with full details
            farmers = Farmer.query.all()
            print(f"\n👨‍🌾 FARMERS TABLE ({len(farmers)} records):")
            print("=" * 80)
            
            if farmers:
                for farmer in farmers:
                    secret_preview = farmer.secret_key[:20] + b'...' if len(farmer.secret_key) > 20 else farmer.secret_key
                    print(f"ID: {farmer.id}")
                    print(f"Phone: {farmer.phone}")
                    print(f"Secret Key: {secret_preview}")
                    print(f"Created: {farmer.created_at}")
                    print(f"Updated: {farmer.updated_at}")
                    print("-" * 80)
            else:
                print("No farmers found.")
            
            # Show Advisories with full details
            advisories = Advisory.query.all()
            print(f"\n📢 ADVISORIES TABLE ({len(advisories)} records):")
            print("=" * 80)
            
            if advisories:
                for advisory in advisories:
                    print(f"ID: {advisory.id}")
                    print(f"Title: {advisory.title}")
                    print(f"Message: {advisory.message}")
                    print(f"Created: {advisory.created_at}")
                    print("-" * 80)
            else:
                print("No advisories found.")
            
            # Show Farming Advisories with full details
            farming_advisories = FarmingAdvisory.query.all()
            print(f"\n📱 FARMING ADVISORIES TABLE ({len(farming_advisories)} records):")
            print("=" * 80)
            
            if farming_advisories:
                for fa in farming_advisories:
                    farmer = Farmer.query.get(fa.farmer_id)
                    advisory = Advisory.query.get(fa.advisory_id)
                    status_icon = "✅" if fa.verified else "⏳"
                    
                    print(f"ID: {fa.id}")
                    print(f"Farmer ID: {fa.farmer_id} ({farmer.phone if farmer else 'Unknown'})")
                    print(f"Advisory ID: {fa.advisory_id} ({advisory.title if advisory else 'Unknown'})")
                    print(f"Sent At: {fa.sent_at}")
                    print(f"Verified: {fa.verified} {status_icon}")
                    print("-" * 80)
            else:
                print("No farming advisory records found.")
                    
    except Exception as e:
        print(f"❌ Error getting all data: {e}")

def show_farmers_table():
    """Show detailed farmers table data"""
    print("👨‍🌾 FARMERS TABLE - DETAILED VIEW:")
    try:
        with get_app_context():
            farmers = Farmer.query.all()
            print("=" * 100)
            
            if farmers:
                # Header
                print(f"{'ID':<4} | {'PHONE':<15} | {'SECRET KEY':<30} | {'CREATED':<20} | {'UPDATED':<20}")
                print("-" * 100)
                
                # Data rows
                for farmer in farmers:
                    secret_preview = farmer.secret_key[:25] + b'...' if len(farmer.secret_key) > 25 else farmer.secret_key
                    created_str = farmer.created_at.strftime('%Y-%m-%d %H:%M') if farmer.created_at else 'N/A'
                    updated_str = farmer.updated_at.strftime('%Y-%m-%d %H:%M') if farmer.updated_at else 'N/A'
                    
                    print(f"{farmer.id:<4} | {farmer.phone:<15} | {str(secret_preview):<30} | {created_str:<20} | {updated_str:<20}")
                
                print("-" * 100)
                print(f"Total: {len(farmers)} farmers")
                
                # Show secret keys in different formats
                print(f"\n🔑 SECRET KEY FORMATS:")
                for farmer in farmers:
                    print(f"Farmer {farmer.id} ({farmer.phone}):")
                    print(f"  Raw bytes: {farmer.secret_key}")
                    print(f"  As UTF-8: {farmer.secret_key.decode('utf-8', errors='ignore')}")
                    print(f"  As Hex: {farmer.secret_key.hex()}")
                    try:
                        import base64
                        print(f"  As Base64: {base64.b64encode(farmer.secret_key).decode('utf-8')}")
                    except:
                        print(f"  As Base64: (conversion error)")
                    print()
                    
            else:
                print("No farmers found.")
                    
    except Exception as e:
        print(f"❌ Error showing farmers table: {e}")

def show_advisories_table():
    """Show detailed advisories table data"""
    print("📢 ADVISORIES TABLE - DETAILED VIEW:")
    try:
        with get_app_context():
            advisories = Advisory.query.all()
            print("=" * 120)
            
            if advisories:
                # Show each advisory in detail
                for advisory in advisories:
                    print(f"ID: {advisory.id}")
                    print(f"Title: {advisory.title}")
                    print(f"Message: {advisory.message}")
                    print(f"Created: {advisory.created_at}")
                    print(f"Message Length: {len(advisory.message)} characters")
                    print("-" * 120)
                
                print(f"Total: {len(advisories)} advisories")
                    
            else:
                print("No advisories found.")
                    
    except Exception as e:
        print(f"❌ Error showing advisories table: {e}")

def show_farming_advisories_table():
    """Show detailed farming advisories table data"""
    print("📱 FARMING ADVISORIES TABLE - DETAILED VIEW:")
    try:
        with get_app_context():
            farming_advisories = FarmingAdvisory.query.all()
            print("=" * 120)
            
            if farming_advisories:
                # Header
                print(f"{'ID':<4} | {'FARMER':<20} | {'ADVISORY':<40} | {'SENT AT':<20} | {'VERIFIED':<10}")
                print("-" * 120)
                
                # Data rows
                for fa in farming_advisories:
                    farmer = Farmer.query.get(fa.farmer_id)
                    advisory = Advisory.query.get(fa.advisory_id)
                    
                    farmer_info = f"{farmer.phone} (ID:{farmer.id})" if farmer else f"Unknown (ID:{fa.farmer_id})"
                    advisory_info = advisory.title[:35] + "..." if advisory and len(advisory.title) > 35 else (advisory.title if advisory else f"Unknown (ID:{fa.advisory_id})")
                    sent_str = fa.sent_at.strftime('%Y-%m-%d %H:%M') if fa.sent_at else 'N/A'
                    verified_icon = "✅ Yes" if fa.verified else "⏳ No"
                    
                    print(f"{fa.id:<4} | {farmer_info:<20} | {advisory_info:<40} | {sent_str:<20} | {verified_icon:<10}")
                
                print("-" * 120)
                print(f"Total: {len(farming_advisories)} farming advisory records")
                    
            else:
                print("No farming advisory records found.")
                    
    except Exception as e:
        print(f"❌ Error showing farming advisories table: {e}")

def main():
    """Main function with command line argument parsing"""
    parser = argparse.ArgumentParser(description='Farmware Database Management')
    
    parser.add_argument('command', choices=[
        'clear-all',
        'clear-farmers', 
        'clear-advisories',
        'create-farmer',
        'create-advisory',
        'create-sample-farmers',
        'create-sample-advisories',
        'delete-farmer',
        'delete-advisory',
        'status',
        'show-all',
        'show-farmers',
        'show-advisories',
        'show-farming-advisories'
    ], help='Command to execute')
    
    # Arguments for create-farmer
    parser.add_argument('--phone', help='Phone number for farmer (required for create-farmer)')
    parser.add_argument('--secret-key', help='Secret key for farmer (required for create-farmer)')
    
    # Arguments for create-advisory
    parser.add_argument('--title', help='Title for advisory (required for create-advisory)')
    parser.add_argument('--message', help='Message for advisory (required for create-advisory)')
    
    # Arguments for delete operations
    parser.add_argument('--id', type=int, help='ID for delete operations (required for delete-farmer/delete-advisory)')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'clear-all':
            clear_database()
            
        elif args.command == 'clear-farmers':
            clear_farmers_table()
            
        elif args.command == 'clear-advisories':
            clear_advisory_table()
            
        elif args.command == 'create-farmer':
            if not args.phone or not args.secret_key:
                print("❌ Error: --phone and --secret-key are required for create-farmer")
                return
            create_farmer(args.phone, args.secret_key)
            
        elif args.command == 'create-advisory':
            if not args.title or not args.message:
                print("❌ Error: --title and --message are required for create-advisory")
                return
            create_advisory(args.title, args.message)
            
        elif args.command == 'create-sample-farmers':
            create_sample_farmers()
            
        elif args.command == 'create-sample-advisories':
            create_sample_advisories()
            
        elif args.command == 'delete-farmer':
            if not args.id:
                print("❌ Error: --id is required for delete-farmer")
                return
            delete_farmer(args.id)
            
        elif args.command == 'delete-advisory':
            if not args.id:
                print("❌ Error: --id is required for delete-advisory")
                return
            delete_advisory(args.id)
            
        elif args.command == 'status':
            show_status()
            
        elif args.command == 'show-all':
            show_all_data()
            
        elif args.command == 'show-farmers':
            show_farmers_table()
            
        elif args.command == 'show-advisories':
            show_advisories_table()
            
        elif args.command == 'show-farming-advisories':
            show_farming_advisories_table()
            
    except Exception as e:
        print(f"❌ Command failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        # No arguments provided, show help
        print("🚀 Farmware Database Management Tool")
        print("\nAvailable commands:")
        print("  clear-all              - Clear entire database")
        print("  clear-farmers          - Clear farmers table only")
        print("  clear-advisories       - Clear advisories table only")
        print("  create-farmer          - Create single farmer (requires --phone --secret-key)")
        print("  create-advisory        - Create single advisory (requires --title --message)")
        print("  create-sample-farmers  - Create sample farmers for testing")
        print("  create-sample-advisories - Create sample advisories for testing")
        print("  delete-farmer          - Delete specific farmer by ID (requires --id)")
        print("  delete-advisory        - Delete specific advisory by ID (requires --id)")
        print("  status                 - Show current database status")
        print("  show-all               - Show all data from all tables (detailed view)")
        print("  show-farmers           - Show detailed farmers table data")
        print("  show-advisories        - Show detailed advisories table data")
        print("  show-farming-advisories - Show detailed farming advisories table data")
        print("\nExamples:")
        print("  python populate_db.py status")
        print("  python populate_db.py clear-all")
        print("  python populate_db.py create-farmer --phone '+254712345678' --secret-key 'FarmwareSecret2024'")
        print("  python populate_db.py create-advisory --title 'Weather Alert' --message 'Rain expected today'")
        print("  python populate_db.py create-sample-farmers")
        print("  python populate_db.py delete-farmer --id 1")
        print("  python populate_db.py delete-advisory --id 2")
        print("  python populate_db.py show-all")
        print("  python populate_db.py show-farmers")
    else:
        main()