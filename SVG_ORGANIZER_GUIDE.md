# SVG Auto-Organizer - User Guide

## What It Does

Takes a flat folder full of SVG files with numbered names and automatically organizes them into logical subfolders.

**Before:**
```
FOLK ART/
├── Bee Folk Art 1.svg
├── Bee Folk Art 2.svg
├── Bee Folk Art 3.svg
├── Butterfly Folk Art 1.svg
├── Butterfly Folk Art 1_1.svg
├── Butterfly Folk Art 2.svg
└── ... (329 files in one folder)
```

**After:**
```
FOLK ART/
├── Bee Folk Art/
│   ├── Bee Folk Art 1.svg
│   ├── Bee Folk Art 2.svg
│   └── Bee Folk Art 3.svg
├── Butterfly Folk Art/
│   ├── Butterfly Folk Art 1.svg
│   ├── Butterfly Folk Art 1_1.svg
│   └── Butterfly Folk Art 2.svg
└── ...
```

## Quick Start

1. Save `svg_auto_organizer.py` to your Scripts folder
2. Run it:
   ```
   python svg_auto_organizer.py
   ```
3. Enter the path to your messy folder
4. Review what it's going to do
5. Type `y` to proceed
6. Done!

## How It Works

**Pattern Detection:**

The script looks at each filename and extracts the "base name" by removing:
- Trailing numbers
- Underscores before numbers
- Spaces before numbers
- File extensions

Examples:
- `Bee Folk Art 1.svg` → Base: "Bee Folk Art"
- `Butterfly_Design_123.svg` → Base: "Butterfly_Design"
- `Simple-Flower-5.svg` → Base: "Simple-Flower"

**Folder Creation:**

Creates one folder per unique base name and moves all matching files into it.

**Filename Preservation:**

Files keep their original names - no renaming. So `Butterfly Folk Art 1.svg` and `Butterfly Folk Art 1_1.svg` both go in the "Butterfly Folk Art" folder with their distinct names.

## Configuration Options

Edit these at the top of the script:

```python
# Only create folders for patterns with at least this many files
MIN_FILES_PER_FOLDER = 1

# Create an "Uncategorized" folder for orphaned files
CREATE_UNCATEGORIZED_FOLDER = True

# Preview mode - shows what would happen without doing it
DRY_RUN = False
```

## Dry Run Mode

**Test before you commit!**

Set `DRY_RUN = True` at the top of the script to see exactly what it would do without actually moving any files.

This shows you:
- Which folders would be created
- Which files would go where
- Any potential issues

Perfect for making sure the pattern detection is working right.

## Common Scenarios

### Single Files

If a pattern only has one file (e.g., "Unique Design 1.svg" with no siblings), by default it still gets its own folder.

**To skip single files:**
Set `MIN_FILES_PER_FOLDER = 2`

### Files Without Numbers

Files like `Dragonfly Folk Art.svg` (no number) are treated as their own base pattern.

### Already Organized Folders

The script only looks at `.svg` files in the root directory you specify - it won't touch existing subfolders.

### Duplicate Folder Names

If a folder already exists, files are added to it (no overwriting).

If a file with the same name already exists in the destination folder, it's skipped with a warning.

## Workflow with SVG Combiner

**Step 1: Organize**
```
python svg_auto_organizer.py
> Enter path: C:\PROJECTS\SVG\FOLK ART
```

**Step 2: Combine**
```
python svg_combiner.py
> Enter path: C:\PROJECTS\SVG\FOLK ART
```

Now you have one organized multi-page Inkscape file!

## Troubleshooting

**"No SVG files found"**
- Make sure you're pointing to the folder containing the SVGs, not a parent folder
- Check that files actually end in `.svg` (not `.SVG` with capital letters - though the script handles this)

**Files going into weird folders**
- Run in DRY_RUN mode first to preview
- Check the pattern detection with a few examples
- Some filenames might have unexpected patterns

**Permission errors**
- Make sure the folder isn't write-protected
- Close any programs that might have files open (Inkscape, Explorer previews, etc.)

**Pattern detection not working right**
- Look at the console output - it shows which base name it detected for each group
- If needed, manually rename a few files to establish clearer patterns
- Or just manually create the folders you want and the script will add files to them

## Tips

**Before running on 329 files:**
- Test on a small subset first (copy 10-20 files to a test folder)
- Use DRY_RUN mode
- Make a backup if you're paranoid (though the script just moves, doesn't delete)

**If you have multiple flat folders:**
Run the script on each one separately, or move all SVGs into one mega-folder first.

**After organizing:**
Your folder structure is now perfect for the SVG combiner script - each subfolder becomes one page.

## Example Output

```
======================================================================
SVG Auto-Organizer
======================================================================

Enter the folder path containing your SVG files:
> C:\PROJECTS\SVG\FOLK ART

Scanning: C:\PROJECTS\SVG\FOLK ART
======================================================================
Found 329 SVG files

Analyzing filename patterns...
Identified 47 unique patterns:

  → Bee Folk Art: 7 file(s)
  → Butterfly Folk Art: 8 file(s)
  → Beetle Folk Art: 5 file(s)
  → Dragonfly Folk Art: 6 file(s)
  ...

======================================================================

Proceed with organizing files? (y/n): y

======================================================================
Organizing files...
======================================================================

Created folder: Bee Folk Art
  ✓ Moved: Bee Folk Art 1.svg
  ✓ Moved: Bee Folk Art 2.svg
  ✓ Moved: Bee Folk Art 3.svg
  ...

======================================================================
✓ ORGANIZATION COMPLETE
======================================================================

Folders created: 47
Files moved: 329
Files skipped: 0

Your files are now organized in: C:\PROJECTS\SVG\FOLK ART

You can now run the SVG combiner script on this folder!
```

## Credits

Created for Emily's flat folder disasters, because extracting SVGs is the easy part - organizing them is where the real pain lives.

## Version History

**v1.0** (March 2025)
- Initial release
- Smart pattern detection
- Dry run mode
- Handles edge cases gracefully
