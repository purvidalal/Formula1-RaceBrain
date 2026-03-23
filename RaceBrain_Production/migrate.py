#!/usr/bin/env python3
"""
Migration Script
Copies your existing working files to the production structure
"""

import os
import shutil
from pathlib import Path

# Paths
OLD_PROJECT = Path.home() / "Downloads" / "RaceBrain_Complete"
NEW_PROJECT = Path.home() / "Downloads" / "RaceBrain_Production"

def copy_directory(src, dst, desc):
    """Copy directory with status message"""
    if src.exists():
        print(f"📁 Copying {desc}...")
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"   ✅ {desc} copied")
    else:
        print(f"   ⚠️  {desc} not found at {src}")

def main():
    print("\n" + "="*60)
    print("🔄 MIGRATING TO PRODUCTION STRUCTURE")
    print("="*60 + "\n")
    
    # Create production directory if needed
    NEW_PROJECT.mkdir(parents=True, exist_ok=True)
    
    # Copy existing working files
    copy_directory(
        OLD_PROJECT / "engine",
        NEW_PROJECT / "engine",
        "Game Engine"
    )
    
    copy_directory(
        OLD_PROJECT / "multi_agent",
        NEW_PROJECT / "multi_agent",
        "Multi-Agent System"
    )
    
    copy_directory(
        OLD_PROJECT / "models",
        NEW_PROJECT / "models",
        "Trained AI Models"
    )
    
    copy_directory(
        OLD_PROJECT / "frontend",
        NEW_PROJECT / "frontend",
        "Frontend Files"
    )
    
    print("\n" + "="*60)
    print("✅ MIGRATION COMPLETE!")
    print("="*60)
    print("\nYour production project is ready at:")
    print(f"📂 {NEW_PROJECT}")
    print("\nNext steps:")
    print("  1. cd ~/Downloads/RaceBrain_Production")
    print("  2. python app/main.py")
    print("  3. Open http://localhost:8000/game")
    print("\n")

if __name__ == "__main__":
    main()
