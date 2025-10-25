#!/usr/bin/env python3
"""
Database migration script to add user_rating and confidence_score columns
to existing analysis_results tables.
"""

import sqlite3
import os
from pathlib import Path

def migrate_database():
    """Add new columns to the analysis_results table if they don't exist."""
    
    # Find the database file
    db_path = Path("cim_analyzer.db")
    if not db_path.exists():
        print("Database file not found. Creating new database...")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns exist
        cursor.execute("PRAGMA table_info(analysis_results)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add user_rating column if it doesn't exist
        if "user_rating" not in columns:
            print("Adding user_rating column...")
            cursor.execute("ALTER TABLE analysis_results ADD COLUMN user_rating REAL")
            print("✓ user_rating column added")
        else:
            print("✓ user_rating column already exists")
        
        # Add confidence_score column if it doesn't exist
        if "confidence_score" not in columns:
            print("Adding confidence_score column...")
            cursor.execute("ALTER TABLE analysis_results ADD COLUMN confidence_score REAL")
            print("✓ confidence_score column added")
        else:
            print("✓ confidence_score column already exists")
        
        # Update users table to use string IDs if needed
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [column[1] for column in cursor.fetchall()]
        
        if "id" in user_columns:
            # Check the type of the id column
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
            table_sql = cursor.fetchone()[0]
            if "INTEGER" in table_sql and "id" in table_sql:
                print("⚠️  Note: Users table still uses INTEGER IDs. Consider recreating the database for Clerk compatibility.")
        
        conn.commit()
        conn.close()
        print("✓ Database migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_database() 