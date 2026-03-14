#!/usr/bin/env python3
"""
APEX Trading Skills - Setup Script

Installs all 32 APEX trading skills to the Hermes skills directory.
"""

import os
import shutil
import json
import sys

SKILLS_SOURCE = os.path.join(os.path.dirname(__file__), "skills", "trading")
SKILLS_DEST = os.path.expanduser("~/.hermes/skills/trading")
APEX_DIR = os.path.expanduser("~/.apex")
CACHE_DIR = os.path.join(APEX_DIR, "cache")
LOGS_DIR = os.path.expanduser("~/.hermes", "logs")

def create_directories():
    """Create required directory structure"""
    print("Creating directories...")
    os.makedirs(CACHE_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    print(f"  Created: {CACHE_DIR}")
    print(f"  Created: {LOGS_DIR}")

def copy_skills():
    """Copy skills to Hermes directory"""
    print(f"\nCopying skills from {SKILLS_SOURCE} to {SKILLS_DEST}...")
    
    if not os.path.exists(SKILLS_SOURCE):
        print(f"ERROR: Skills source not found: {SKILLS_SOURCE}")
        sys.exit(1)
    
    # Create destination if needed
    os.makedirs(SKILLS_DEST, exist_ok=True)
    
    # Copy each skill
    skill_count = 0
    for item in os.listdir(SKILLS_SOURCE):
        src = os.path.join(SKILLS_SOURCE, item)
        dst = os.path.join(SKILLS_DEST, item)
        
        if os.path.isdir(src) and item.startswith("apex-"):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            skill_count += 1
            print(f"  Copied: {item}")
    
    print(f"  Total skills copied: {skill_count}")
    return skill_count

def create_state_file():
    """Create state.json from template"""
    print("\nCreating state.json...")
    
    state_file = os.path.join(APEX_DIR, "state.json")
    
    if os.path.exists(state_file):
        response = input("  state.json already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("  Keeping existing state.json")
            return
    
    template = os.path.join(os.path.dirname(__file__), "config", "state.template.json")
    
    if os.path.exists(template):
        shutil.copy(template, state_file)
        print(f"  Created: {state_file}")
        print("  IMPORTANT: Edit this file with your Dhan API credentials!")
    else:
        print(f"  ERROR: Template not found: {template}")

def verify_setup():
    """Verify installation"""
    print("\nVerifying setup...")
    
    # Check skills
    if os.path.exists(SKILLS_DEST):
        skills = [d for d in os.listdir(SKILLS_DEST) if d.startswith("apex-")]
        print(f"  Skills installed: {len(skills)}")
    else:
        print("  ERROR: Skills directory not found!")
    
    # Check state file
    state_file = os.path.join(APEX_DIR, "state.json")
    if os.path.exists(state_file):
        print(f"  State file: {state_file}")
    else:
        print("  WARNING: State file not found")
    
    # Check cache
    if os.path.exists(CACHE_DIR):
        print(f"  Cache directory: {CACHE_DIR}")

def main():
    print("=" * 60)
    print("APEX Trading Skills - Setup")
    print("=" * 60)
    
    # Create directories
    create_directories()
    
    # Copy skills
    skill_count = copy_skills()
    
    # Create state file
    create_state_file()
    
    # Verify
    verify_setup()
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)
    print(f"\nNext steps:")
    print("1. Edit ~/.apex/state.json with your Dhan API credentials")
    print("2. Copy .env.example to .env and fill in values")
    print("3. Test with: python3 ~/.hermes/skills/trading/apex-india-vix-monitor/fetch_vix.py")
    print("\nFor cronjob setup, see SETUP.md")

if __name__ == "__main__":
    main()