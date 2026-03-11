#!/usr/bin/env python3
"""
CLI tool for database management
"""

import sys
import argparse
from database import init_db, drop_db
from database.seed import seed_all


def main():
    parser = argparse.ArgumentParser(description="Schedulo Database CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Init command
    subparsers.add_parser("init", help="Initialize database tables")

    # Drop command
    subparsers.add_parser("drop", help="Drop all database tables")

    # Seed command
    subparsers.add_parser("seed", help="Seed database with sample data")

    # Reset command
    subparsers.add_parser("reset", help="Drop, init, and seed database")

    args = parser.parse_args()

    if args.command == "init":
        print("🔧 Initializing database...")
        init_db()
        print("✅ Database initialized!")

    elif args.command == "drop":
        confirm = input("⚠️  Are you sure you want to drop all tables? (yes/no): ")
        if confirm.lower() == "yes":
            drop_db()
            print("✅ Database dropped!")
        else:
            print("❌ Cancelled")

    elif args.command == "seed":
        print("🌱 Seeding database...")
        seed_all()

    elif args.command == "reset":
        confirm = input("⚠️  This will delete all data. Continue? (yes/no): ")
        if confirm.lower() == "yes":
            print("🔧 Resetting database...")
            drop_db()
            init_db()
            seed_all()
            print("✅ Database reset complete!")
        else:
            print("❌ Cancelled")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
