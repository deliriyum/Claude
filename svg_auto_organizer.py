"""
SVG Auto-Organizer
==================

Organizes flat folders full of SVG files into logical subfolders based on filename patterns.

USE CASE:
You extracted a bunch of SVGs from various sources and now have a flat folder with 
hundreds of files like:
    Bee Folk Art 1.svg
    Bee Folk Art 2.svg
    Butterfly Folk Art 1.svg
    Butterfly Folk Art 1_1.svg
    ...

This script:
- Detects the base name pattern (e.g., "Bee Folk Art", "Butterfly Folk Art")
- Creates folders for each pattern
- Moves files into their appropriate folders
- Preserves original filenames (no renaming)
- Handles edge cases gracefully

Created by: Emily (maker/fabricator) with assistance from Claude (AI)
For organizing all those flat SVG folder disasters.

License: MIT
Version: 1.0
Date: March 2025
"""

import os
import re
import shutil
from pathlib import Path
from collections import defaultdict

# ============================================================================
# CONFIGURATION SECTION
# ============================================================================

# Minimum number of files that must match a pattern to create a folder
# Set to 1 to organize everything, or higher to only organize groups
MIN_FILES_PER_FOLDER = 1

# Whether to create an "Uncategorized" folder for files that don't match any pattern
CREATE_UNCATEGORIZED_FOLDER = True

# Dry run mode - if True, shows what would happen without actually moving files
DRY_RUN = False

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_base_name(filename):
    """
    Extract the base pattern from a filename by removing trailing numbers and extensions.
    
    Handles the pattern where _# indicates different design sets:
    - "Moth 1.svg", "Moth 2.svg" → "Moth" (design set A)
    - "Moth 1_1.svg", "Moth 2_1.svg" → "Moth_1" (design set B) 
    - "Moth 1_2.svg", "Moth 2_2.svg" → "Moth_2" (design set C)
    
    Examples:
        "Bee Folk Art 1.svg" → "Bee Folk Art"
        "Butterfly Folk Art 1_1.svg" → "Butterfly Folk Art_1"
        "Butterfly Folk Art 2_1.svg" → "Butterfly Folk Art_1"
        "Butterfly Folk Art 1_2.svg" → "Butterfly Folk Art_2"
        "Dragonfly Folk Art.svg" → "Dragonfly Folk Art"
        "Simple_Design_123.svg" → "Simple_Design"
    
    Args:
        filename: The filename to process (string)
        
    Returns:
        Base name that groups files by their design set (string)
    """
    # Remove the file extension
    name_without_ext = Path(filename).stem
    
    # Check if this follows the "Name #_#" pattern (separate design sets)
    # Pattern: [name] [digit(s)] _ [digit(s)]
    # Example: "Moth 1_1" → groups = ("Moth ", "1", "1")
    underscore_pattern = re.match(r'^(.+?)\s*(\d+)_(\d+)$', name_without_ext)
    
    if underscore_pattern:
        # This is a "Name #_#" pattern
        # Group by the base name + the second number (after underscore)
        base_part = underscore_pattern.group(1).strip()
        set_number = underscore_pattern.group(3)  # The number after underscore
        base_name = f"{base_part}_{set_number}"
    else:
        # Standard pattern - just remove trailing numbers
        # This regex matches: optional separator + one or more digits at the end
        # Examples: " 1", "_2", "-3", " 123", etc.
        base_name = re.sub(r'[\s_-]*\d+$', '', name_without_ext)
        
        # Clean up any trailing spaces or underscores
        base_name = base_name.strip().rstrip('_-')
    
    # If we stripped everything (file was just numbers), use original name
    if not base_name:
        base_name = name_without_ext
    
    return base_name


def group_files_by_pattern(svg_files):
    """
    Group SVG files by their base name pattern.
    
    Args:
        svg_files: List of Path objects pointing to SVG files
        
    Returns:
        Dictionary where keys are base names and values are lists of file paths
        Example: {"Bee Folk Art": [Path("Bee Folk Art 1.svg"), Path("Bee Folk Art 2.svg")]}
    """
    groups = defaultdict(list)
    
    for svg_file in svg_files:
        base_name = extract_base_name(svg_file.name)
        groups[base_name].append(svg_file)
    
    return dict(groups)


def sanitize_folder_name(name):
    """
    Clean up a folder name to be filesystem-safe.
    
    Removes/replaces characters that are problematic on Windows/Mac/Linux:
    - Invalid characters: < > : " / \ | ? *
    - Leading/trailing spaces and periods
    
    Args:
        name: The proposed folder name
        
    Returns:
        Sanitized folder name safe for all major filesystems
    """
    # Replace invalid characters with underscores
    invalid_chars = r'[<>:"/\\|?*]'
    clean_name = re.sub(invalid_chars, '_', name)
    
    # Remove leading/trailing spaces and periods
    clean_name = clean_name.strip().strip('.')
    
    # Collapse multiple underscores
    clean_name = re.sub(r'_+', '_', clean_name)
    
    # If we somehow ended up with an empty name, use a default
    if not clean_name:
        clean_name = "Unnamed"
    
    return clean_name


def organize_files(root_path, groups, dry_run=False):
    """
    Create folders and move files into them based on grouping.
    
    Args:
        root_path: Path object pointing to the root directory
        groups: Dictionary of {base_name: [file_paths]} from group_files_by_pattern
        dry_run: If True, print what would happen without actually doing it
        
    Returns:
        Dictionary with statistics about the operation
    """
    stats = {
        'folders_created': 0,
        'files_moved': 0,
        'files_skipped': 0,
        'errors': []
    }
    
    for base_name, files in groups.items():
        # Skip if this group doesn't meet minimum file threshold
        if len(files) < MIN_FILES_PER_FOLDER:
            stats['files_skipped'] += len(files)
            continue
        
        # Create the folder name
        folder_name = sanitize_folder_name(base_name)
        folder_path = root_path / folder_name
        
        # Create the folder if it doesn't exist
        if dry_run:
            print(f"[DRY RUN] Would create folder: {folder_path}")
        else:
            try:
                folder_path.mkdir(exist_ok=True)
                stats['folders_created'] += 1
                print(f"Created folder: {folder_name}")
            except Exception as e:
                error_msg = f"Error creating folder {folder_name}: {e}"
                stats['errors'].append(error_msg)
                print(f"✗ {error_msg}")
                continue
        
        # Move files into the folder
        for file_path in files:
            destination = folder_path / file_path.name
            
            if dry_run:
                print(f"  [DRY RUN] Would move: {file_path.name} → {folder_name}/")
            else:
                try:
                    # Check if destination already exists
                    if destination.exists():
                        print(f"  ⚠ Skipping {file_path.name} - already exists in {folder_name}/")
                        stats['files_skipped'] += 1
                        continue
                    
                    # Move the file
                    shutil.move(str(file_path), str(destination))
                    stats['files_moved'] += 1
                    print(f"  ✓ Moved: {file_path.name}")
                    
                except Exception as e:
                    error_msg = f"Error moving {file_path.name}: {e}"
                    stats['errors'].append(error_msg)
                    print(f"  ✗ {error_msg}")
    
    return stats


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main function - orchestrates the organization process.
    """
    print("=" * 70)
    print("SVG Auto-Organizer")
    print("=" * 70)
    print()
    
    # Get the directory to organize
    if DRY_RUN:
        print("🔍 DRY RUN MODE - No files will actually be moved")
        print()
    
    root_dir = input("Enter the folder path containing your SVG files:\n> ").strip()
    root_dir = root_dir.strip('"').strip("'")  # Remove quotes if copied from explorer
    
    root_path = Path(root_dir)
    
    # Validate path
    if not root_path.exists():
        print(f"\n✗ Error: Path does not exist: {root_path}")
        input("\nPress Enter to exit...")
        return
    
    if not root_path.is_dir():
        print(f"\n✗ Error: Path is not a directory: {root_path}")
        input("\nPress Enter to exit...")
        return
    
    print(f"\nScanning: {root_path}")
    print("=" * 70)
    
    # Find all SVG files in the root directory (not subdirectories)
    svg_files = list(root_path.glob("*.svg"))
    
    if not svg_files:
        print("\n✗ No SVG files found in this directory!")
        input("\nPress Enter to exit...")
        return
    
    print(f"Found {len(svg_files)} SVG files")
    print()
    
    # Group files by pattern
    print("Analyzing filename patterns...")
    groups = group_files_by_pattern(svg_files)
    
    print(f"Identified {len(groups)} unique patterns:")
    print()
    
    # Show what will be created
    for base_name, files in sorted(groups.items(), key=lambda x: len(x[1]), reverse=True):
        folder_name = sanitize_folder_name(base_name)
        file_count = len(files)
        
        if file_count < MIN_FILES_PER_FOLDER:
            print(f"  ⊘ {folder_name}: {file_count} file(s) - SKIP (below minimum)")
        else:
            print(f"  → {folder_name}: {file_count} file(s)")
    
    print()
    print("=" * 70)
    
    # Confirm before proceeding
    if DRY_RUN:
        response = input("\nRun dry-run analysis? (y/n): ").strip().lower()
    else:
        response = input("\nProceed with organizing files? (y/n): ").strip().lower()
    
    if response != 'y':
        print("\nOperation cancelled.")
        input("\nPress Enter to exit...")
        return
    
    print()
    print("=" * 70)
    print("Organizing files...")
    print("=" * 70)
    print()
    
    # Do the organization
    stats = organize_files(root_path, groups, dry_run=DRY_RUN)
    
    # Report results
    print()
    print("=" * 70)
    if DRY_RUN:
        print("✓ DRY RUN COMPLETE")
    else:
        print("✓ ORGANIZATION COMPLETE")
    print("=" * 70)
    print()
    print(f"Folders created: {stats['folders_created']}")
    print(f"Files moved: {stats['files_moved']}")
    print(f"Files skipped: {stats['files_skipped']}")
    
    if stats['errors']:
        print(f"\n⚠ Errors encountered: {len(stats['errors'])}")
        for error in stats['errors']:
            print(f"  - {error}")
    
    if not DRY_RUN:
        print(f"\nYour files are now organized in: {root_path}")
        print("\nYou can now run the SVG combiner script on this folder!")
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
