# SVG Multi-Page Combiner - User Guide

## What This Script Does

This Python script takes a messy directory structure full of SVG files and combines them into **one organized Inkscape document** with multiple pages.

**Two Modes Available:**

**Stack Mode (Default):** Each parent folder becomes one page with all SVG files from that folder stacked as layers, centered on the page.

**Tile Mode:** All SVG files are collected and tiled across multiple pages in a grid layout, with each SVG scaled to fit within a tile while maintaining aspect ratio. Perfect for when you have many individual patterns that need to be arranged efficiently on standard-sized pages.

**Key Features:**
- Handles mixed directory structures (nested folders or flat)
- Natural sorting (handles name_1, name 1, name-01, etc.)
- Automatic scaling and positioning
- Dynamic output naming based on root folder
- Preserves original SVG content and styling

---

## Quick Start (The TL;DR Version)

1. Save `svg_combiner.py` somewhere easy to find (like your Desktop or Documents)
2. Double-click the script
3. Paste in your root folder path when asked
4. Press Enter and let it run
5. Open `Hex_Signs_ALL.svg` in Inkscape

Done!

---

## Detailed Instructions

### First Time Setup

**Prerequisites:**
- Python 3.x installed (you have 3.14.2 ✓)
- lxml library installed (you have this ✓)

If you ever need to use this on another computer, install lxml with:
```
python -m pip install lxml
```

### Running The Script

**Method 1: Double-Click (Easiest)**

1. Save `svg_combiner.py` to somewhere convenient
2. Double-click the file
3. Windows will open a command window
4. The script will ask: "Enter the root folder path containing your SVG files:"
5. Paste your path (like `C:\Projects\FOLK ART\HEX SIGNS`)
6. Press Enter

**Method 2: Command Line**

1. Open Command Prompt (cmd)
2. Navigate to where you saved the script:
   ```
   cd C:\path\to\script\location
   ```
3. Run:
   ```
   python svg_combiner.py
   ```
4. Follow the prompts

**Method 3: Drag and Drop**

1. Open Command Prompt
2. Type `python ` (with a space after)
3. Drag `svg_combiner.py` into the cmd window
4. Press Enter
5. Follow the prompts

---

## What Happens When You Run It

### Step 1: Scanning
The script walks through your entire directory structure and finds all `.svg` files.

**Stack Mode:** Groups them by parent folder.
**Tile Mode:** Collects all SVGs for tiling.

**Example output (Stack Mode):**
```
Found 6 SVG files in 'Pennsylvania-Dutch-Hex-Sign-33272525'
Found 5 SVG files in 'Pennsylvania-Dutch-Hex-Sign-Birds-and-heart-layered-design-Crafts'
...
```

**Example output (Tile Mode):**
```
Found 102 SVG files total
Tile layout: 9 columns x 9 rows = 81 SVGs per page
```

### Step 2: Confirmation
It shows you what it found and asks if you want to proceed:

**Stack Mode:**
```
Found 19 parent folders with SVG files
Total SVG files to process: 102

Create 'Hex_Signs_ALL.svg' with 102 SVGs stacked as layers? (y/n):
```

**Tile Mode:**
```
Found 102 SVG files total
Total SVG files to process: 102

Create 'Hex_Signs_ALL.svg' with 102 SVGs tiled on pages? (y/n):
```

Type `y` and press Enter.

### Step 3: Processing

**Stack Mode:** The script processes each parent folder as a page:
```
Processing page 1: Pennsylvania-Dutch-Hex-Sign-33272525
  Adding 6 layers...
    - hex_sign_1
    - hex_sign_2
    ...
```

**Tile Mode:** SVGs are arranged in a grid across pages:
```
Processing page 1: SVGs 1 to 81
    - pattern_1
    - pattern_2
    ...
Processing page 2: SVGs 82 to 102
    - pattern_82
    ...
```

### Step 4: Done!
```
✓ Successfully created C:\Projects\FOLK ART\HEX SIGNS\Hex_Signs_ALL.svg
  Total pages: 19
```

---

## Opening Your Combined File

1. Open Inkscape
2. File → Open
3. Navigate to your root folder
4. Open `Hex_Signs_ALL.svg`

**You'll see:**
- Multiple pages (use the page selector at the bottom)
- **Stack Mode:** Each page has multiple layers (visible in Layers panel)
- **Tile Mode:** Each page has a grid of scaled SVGs
- All content is properly positioned on 12×12 inch pages
- Layers are named after their source files

**To navigate pages in Inkscape:**
- Use the page selector at the bottom of the window
- Or: View → Page → Next/Previous

---

## Customizing The Script

All the important settings are at the top of the file in the **CONFIGURATION SECTION**:

```python
# Output filename (will be saved in the root directory you specify)
OUTPUT_FILENAME = "Hex_Signs_ALL.svg"

# Page dimensions in inches
PAGE_WIDTH = 12
PAGE_HEIGHT = 12

# DPI for converting inches to pixels (Inkscape default)
DPI = 96

# Mode: "stack" or "tile"
# "stack": Each parent folder becomes one page with SVGs stacked as layers (original behavior)
# "tile": All SVGs are tiled on pages with margins, fitting as many as possible per page
MODE = "tile"

# Tile mode settings (only used if MODE = "tile")
TILE_MARGIN = 0.5  # inches between tiles
TILE_WIDTH = 2.0   # inches width for each tile (SVGs will be scaled to fit)
TILE_HEIGHT = 2.0  # inches height for each tile
```

**Common Changes:**

### Switch to Tile Mode
If you want to tile SVGs instead of stacking them:
```python
MODE = "tile"
```

In tile mode, all SVGs from all subfolders are collected and arranged on pages in a grid, with each SVG scaled to fit within the tile size while maintaining aspect ratio.

### Adjust Tile Settings
For smaller tiles (fits more per page):
```python
TILE_WIDTH = 1.5
TILE_HEIGHT = 1.5
TILE_MARGIN = 0.25
```

For larger tiles (fewer per page):
```python
TILE_WIDTH = 3.0
TILE_HEIGHT = 3.0
TILE_MARGIN = 0.5
```

### Change Output Filename
```python
OUTPUT_FILENAME = "My_Combined_File.svg"
```

### Change Page Size
For letter-size pages:
```python
```python
PAGE_WIDTH = 8.5
PAGE_HEIGHT = 11
```

For A4:
```python
PAGE_WIDTH = 8.27
PAGE_HEIGHT = 11.69
```

### Change DPI
If your SVGs use a different DPI:
```python
DPI = 72  # or 300 for high-res
```

Just edit these values, save the file, and run it again!

---

## Troubleshooting

### "python is not recognized..."
- Python isn't in your PATH
- Try: `python3` instead of `python`
- Or reinstall Python and check "Add Python to PATH"

### "No module named 'lxml'"
- Run: `python -m pip install lxml`

### "No SVG files found!"
- Check your path - make sure it's the root folder containing all your parent folders
- Make sure your files actually end in `.svg` (not `.SVG` - but the script handles this)

### SVGs look weird or missing in output
- Some SVGs might have unusual formatting
- Open the problematic file in Inkscape and re-save it
- Or: Edit the script to skip problematic files (I can help with this)

### "Permission denied" error
- Make sure the output location isn't write-protected
- Try running Command Prompt as Administrator

---

## Advanced Usage

### Processing a Different Folder

Just run the script again and give it a new path. You can reuse it for any project with a similar structure.

### Batch Processing Multiple Root Folders

Create a simple batch file (`combine_all.bat`):
```batch
@echo off
python svg_combiner.py "C:\Path\To\Folder1"
python svg_combiner.py "C:\Path\To\Folder2"
python svg_combiner.py "C:\Path\To\Folder3"
pause
```

Double-click the batch file and it'll process all three folders automatically.

### Changing Layer Stacking

Currently, all layers are centered and overlapping. If you want them spaced out vertically instead, find this line in the script:

```python
"transform": f"translate({offset_x}, {offset_y})"
```

And change it to:
```python
"transform": f"translate({offset_x}, {offset_y + (idx * 100)})"
```

This spaces each layer 100 pixels below the previous one.

---

## How The Script Works (Technical Overview)

For future reference or if you want to modify it:

### 1. Directory Scanning (`find_all_svgs`)
- Uses `pathlib` to recursively walk the directory tree
- `rglob("*.svg")` finds all SVG files regardless of nesting
- Groups files by immediate parent folder
- Sorts using natural sorting (handles numbers correctly)

### 2. SVG Parsing (`get_svg_viewbox`)
- Uses `lxml.etree` to parse XML
- Extracts viewBox or width/height attributes
- Handles unit conversion (removes 'px', 'in', etc.)
- Falls back to page size if dimensions not found

### 3. Layer Creation (`create_centered_layer`)
- Parses each source SVG
- Calculates centering transform
- Creates an Inkscape layer (`<g>` element with layer attributes)
- Copies all child elements from source
- Skips metadata to keep file clean

### 4. Document Assembly (`create_multipage_svg`)
- Creates root SVG element with proper namespaces
- Adds Inkscape-specific elements for multi-page support
- Creates page groups (each parent folder = one page)
- Adds layers to pages
- Writes formatted XML output

### 5. Main Loop
- Handles user input
- Validates paths
- Orchestrates the whole process
- Provides progress feedback

---

## File Structure Reference

**Input Structure (what you have):**
```
HEX SIGNS/
├── Design_A/
│   ├── layer1/
│   │   └── file.svg
│   └── layer2/
│       └── file.svg
├── Design_B/
│   ├── file1.svg
│   ├── file2.svg
│   └── file3.svg
└── ...
```

**Output Structure (what you get):**
```xml
<svg> <!-- Root document -->
  <g inkscape:label="Page 1: Design_A"> <!-- Page 1 -->
    <g inkscape:label="file1"> <!-- Layer 1 -->
      <!-- SVG content centered -->
    </g>
    <g inkscape:label="file2"> <!-- Layer 2 -->
      <!-- SVG content centered -->
    </g>
  </g>
  <g inkscape:label="Page 2: Design_B"> <!-- Page 2 -->
    <!-- More layers... -->
  </g>
</svg>
```

---

## Future Enhancements (Ideas)

If you want to expand this script later:

1. **Add preview mode** - Generate thumbnails before combining
2. **Layer visibility control** - Hide certain layers by default
3. **Custom page assignments** - Config file to control which files go on which pages
4. **Size detection** - Automatically adjust page size based on content
5. **Style preservation** - Better handling of embedded styles and fonts
6. **Error recovery** - Skip problematic files instead of failing
7. **GUI version** - Drag-and-drop interface with preview

Let me know if you want any of these features added!

---

## Credits

Created for Emily's hex sign combining project, December 2024.

Feel free to modify, share, or use this for any project. If you make cool improvements, I'd love to hear about them!

---

## Quick Reference Card

**Installation:**
```
python -m pip install lxml
```

**Run Script:**
```
python svg_combiner.py
```

**Change Settings:**
Edit lines 18-24 in `svg_combiner.py`

**Output Location:**
Same folder as your input files, named `Hex_Signs_ALL.svg`

**Questions?**
Just ask! I'm happy to help troubleshoot or add features.
