"""
SVG Multi-Page Combiner
-----------------------
This script recursively finds all SVG files in a directory structure,
groups them by parent folder, and combines them into a single multi-page
Inkscape document with each parent folder's SVGs on its own page.

Author: Created for Emily's hex sign project
Date: December 2024
"""

import os
import sys
from pathlib import Path
from lxml import etree
import re

# ============================================================================
# CONFIGURATION SECTION - Change these settings as needed
# ============================================================================

# Output filename options:
# - Set to None to use root folder name + "_ALL.svg"
# - Set to "ASK" to prompt user for filename
# - Set to specific name like "My_Design.svg" to use that
OUTPUT_FILENAME = None  # Will use folder name + "_ALL.svg"

# Page dimensions in inches
PAGE_WIDTH = 12
PAGE_HEIGHT = 12

# DPI for converting inches to pixels (Inkscape default)
DPI = 96

# Calculate page dimensions in pixels
PAGE_WIDTH_PX = PAGE_WIDTH * DPI
PAGE_HEIGHT_PX = PAGE_HEIGHT * DPI

# Mode: "stack" or "tile"
# "stack": Each parent folder becomes one page with SVGs stacked as layers (original behavior)
# "tile": All SVGs are tiled on pages with margins, fitting as many as possible per page
MODE = "STACK"

# Tile mode settings (only used if MODE = "tile")
TILE_MARGIN = 0.5  # inches between tiles
TILE_WIDTH = 2.0   # inches width for each tile (SVGs will be scaled to fit)
TILE_HEIGHT = 2.0  # inches height for each tile

# SVG namespace - needed for proper XML handling
SVG_NS = "http://www.w3.org/2000/svg"
INKSCAPE_NS = "http://www.inkscape.org/namespaces/inkscape"
SODIPODI_NS = "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"

# Register namespaces
etree.register_namespace('svg', SVG_NS)
etree.register_namespace('inkscape', INKSCAPE_NS)
etree.register_namespace('sodipodi', SODIPODI_NS)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def natural_sort_key(text):
    """
    Sort strings containing numbers naturally (1, 2, 10 instead of 1, 10, 2)
    Handles various naming conventions like name_1, name 1, name-1, name01
    """
    def atoi(text):
        return int(text) if text.isdigit() else text.lower()
    
    return [atoi(c) for c in re.split(r'(\d+)', str(text))]


def parse_svg_styles(svg_root):
    """
    Extract CSS styles from <style> blocks in an SVG.
    
    Many SVG editors (like Adobe Illustrator) define colors in CSS classes:
    <style>.st0{fill:#F7E054;}</style>
    <path class="st0" .../>
    
    This function parses those styles into a dictionary so we can apply them inline.
    
    Args:
        svg_root: lxml Element representing the SVG root
        
    Returns:
        Dictionary mapping class names to style properties
        Example: {"st0": {"fill": "#F7E054", "stroke": "#000000"}}
    """
    styles = {}
    
    # Find all <style> elements
    for style_elem in svg_root.findall(f".//{{{SVG_NS}}}style"):
        if style_elem.text:
            css_text = style_elem.text
            
            # Parse CSS rules - very basic parser for .classname{property:value;}
            # Matches patterns like: .st0{fill:#F7E054;stroke:#000000;}
            class_pattern = r'\.([a-zA-Z0-9_-]+)\s*\{([^}]+)\}'
            
            for match in re.finditer(class_pattern, css_text):
                class_name = match.group(1)
                properties_text = match.group(2)
                
                # Parse individual properties
                properties = {}
                for prop in properties_text.split(';'):
                    prop = prop.strip()
                    if ':' in prop:
                        key, value = prop.split(':', 1)
                        properties[key.strip()] = value.strip()
                
                styles[class_name] = properties
    
    return styles


def apply_inline_styles(element, styles_dict):
    """
    Recursively apply CSS class styles as inline attributes.
    
    Converts: <path class="st0" .../>
    To: <path fill="#F7E054" .../>
    
    Args:
        element: lxml Element to process
        styles_dict: Dictionary of class definitions from parse_svg_styles
    """
    # Check if this element has a class attribute
    class_attr = element.get('class')
    
    if class_attr and class_attr in styles_dict:
        style_props = styles_dict[class_attr]
        
        # Apply each CSS property as an inline attribute
        for prop, value in style_props.items():
            # Only set the attribute if it doesn't already exist
            # (explicit attributes take precedence over classes)
            if element.get(prop) is None:
                element.set(prop, value)
        
        # Remove the class attribute since we've converted it to inline styles
        del element.attrib['class']
    
    # Recursively process children
    for child in element:
        apply_inline_styles(child, styles_dict)


def find_all_svgs(root_path, mode="stack"):
    """
    Recursively find all SVG files in the directory structure.
    
    For "stack" mode: Groups them by their immediate parent folder.
    For "tile" mode: Returns all SVGs in one flat list.
    
    Returns: Dictionary with keys as group names, values as lists of SVG file paths
    """
    root_path = Path(root_path)
    
    if mode == "tile":
        all_svgs = []
        # Walk through all subdirectories and collect all SVGs
        for svg_file in root_path.rglob("*.svg"):
            all_svgs.append(svg_file)
        
        # Sort files naturally by name
        all_svgs.sort(key=lambda x: natural_sort_key(x.name))
        
        if all_svgs:
            print(f"Found {len(all_svgs)} SVG files total")
            return {"All_SVGs": all_svgs}
        else:
            return {}
    
    else:  # stack mode
        svg_groups = {}
        
        # Walk through all subdirectories
        for parent_dir in root_path.iterdir():
            if not parent_dir.is_dir():
                continue
                
            parent_name = parent_dir.name
            svg_files = []
            
            # Recursively find all SVG files under this parent
            for svg_file in parent_dir.rglob("*.svg"):
                svg_files.append(svg_file)
            
            # Sort files naturally by name
            svg_files.sort(key=lambda x: natural_sort_key(x.name))
            
            if svg_files:
                svg_groups[parent_name] = svg_files
                print(f"Found {len(svg_files)} SVG files in '{parent_name}'")
        
        return svg_groups


def get_svg_viewbox(svg_path):
    """
    Extract viewBox or width/height from an SVG file.
    Returns (width, height) in pixels.
    """
    try:
        tree = etree.parse(str(svg_path))
        root = tree.getroot()
        
        # Try to get viewBox first
        viewbox = root.get('viewBox')
        if viewbox:
            parts = viewbox.split()
            if len(parts) == 4:
                return float(parts[2]), float(parts[3])
        
        # Fall back to width/height attributes
        width = root.get('width')
        height = root.get('height')
        
        if width and height:
            # Remove units and convert to float
            width = float(re.sub(r'[^0-9.]', '', width))
            height = float(re.sub(r'[^0-9.]', '', height))
            return width, height
        
        # Default if nothing found
        return PAGE_WIDTH_PX, PAGE_HEIGHT_PX
        
    except Exception as e:
        print(f"Warning: Could not read dimensions from {svg_path.name}: {e}")
        return PAGE_WIDTH_PX, PAGE_HEIGHT_PX


def create_tiled_layer(svg_path, layer_name, x_offset, y_offset, scale):
    """
    Load an SVG file and create a scaled and positioned layer group for it.
    Used in tile mode. Now preserves colors from CSS styles.
    Returns an lxml Element representing the layer.
    """
    try:
        # Parse the source SVG
        tree = etree.parse(str(svg_path))
        root = tree.getroot()
        
        # Parse any CSS styles from <style> blocks
        styles_dict = parse_svg_styles(root)
        
        # Get the SVG's dimensions
        svg_width, svg_height = get_svg_viewbox(svg_path)
        
        # Create a group (layer) for this SVG
        layer = etree.Element(
            f"{{{SVG_NS}}}g",
            attrib={
                f"{{{INKSCAPE_NS}}}groupmode": "layer",
                f"{{{INKSCAPE_NS}}}label": layer_name,
                "id": f"layer_{layer_name.replace(' ', '_')}",
                "transform": f"translate({x_offset}, {y_offset}) scale({scale})"
            }
        )
        
        # Copy all child elements from the source SVG into this layer
        for child in root:
            # Skip metadata, defs, and style blocks
            if child.tag.endswith(('metadata', 'namedview', 'style')):
                continue
            
            # Make a copy of the element
            child_copy = etree.fromstring(etree.tostring(child))
            
            # Apply inline styles if we found any CSS classes
            if styles_dict:
                apply_inline_styles(child_copy, styles_dict)
            
            layer.append(child_copy)
        
        return layer
        
    except Exception as e:
        print(f"Error processing {svg_path.name}: {e}")
        return None


def create_centered_layer(svg_path, layer_name, page_num, layer_idx=0):
    """
    Load an SVG file and create a scaled, centered layer group for it.
    Used in stack mode. Scales to fit within an 11x11in area (0.5in margin
    on all sides) and centers on the 12x12in page. Preserves CSS colors.
    Returns an lxml Element representing the layer.
    """
    try:
        # Parse the source SVG
        tree = etree.parse(str(svg_path))
        root = tree.getroot()

        # Parse any CSS styles from <style> blocks
        styles_dict = parse_svg_styles(root)

        # Get the SVG's dimensions
        svg_width, svg_height = get_svg_viewbox(svg_path)

        # Scale to fit within 11x11in (0.5in margin each side), maintain aspect ratio
        margin_px = 0.5 * DPI
        target_px = PAGE_WIDTH_PX - 2 * margin_px  # 11 inches worth of pixels
        if svg_width > 0 and svg_height > 0:
            scale = min(target_px / svg_width, target_px / svg_height)
        else:
            scale = 1.0

        # Center the scaled content on the page
        offset_x = (PAGE_WIDTH_PX - svg_width * scale) / 2
        offset_y = (PAGE_HEIGHT_PX - svg_height * scale) / 2

        # Create a group (layer) for this SVG — include layer_idx to guarantee unique IDs
        layer = etree.Element(
            f"{{{SVG_NS}}}g",
            attrib={
                f"{{{INKSCAPE_NS}}}groupmode": "layer",
                f"{{{INKSCAPE_NS}}}label": layer_name,
                "id": f"layer_{page_num}_{layer_idx}_{layer_name.replace(' ', '_')}",
                "transform": f"translate({offset_x}, {offset_y}) scale({scale})"
            }
        )
        
        # Copy all child elements from the source SVG into this layer
        for child in root:
            # Skip metadata, defs, and style blocks
            if child.tag.endswith(('metadata', 'namedview', 'style')):
                continue
            
            # Make a copy of the element
            child_copy = etree.fromstring(etree.tostring(child))
            
            # Apply inline styles if we found any CSS classes
            if styles_dict:
                apply_inline_styles(child_copy, styles_dict)
            
            layer.append(child_copy)
        
        return layer
        
    except Exception as e:
        print(f"Error processing {svg_path.name}: {e}")
        return None


def create_multipage_svg(svg_groups, output_path, mode="stack"):
    """
    Create a multi-page Inkscape SVG document.
    
    For "stack" mode: Each group contains all SVGs from one parent folder as layers on one page.
    For "tile" mode: All SVGs are tiled across multiple pages.
    """
    # Calculate tile parameters if in tile mode
    if mode == "tile":
        TILE_MARGIN_PX = TILE_MARGIN * DPI
        TILE_WIDTH_PX = TILE_WIDTH * DPI
        TILE_HEIGHT_PX = TILE_HEIGHT * DPI
        
        available_width_px = PAGE_WIDTH_PX - TILE_MARGIN_PX * 2
        available_height_px = PAGE_HEIGHT_PX - TILE_MARGIN_PX * 2
        
        cols = max(1, int(available_width_px // (TILE_WIDTH_PX + TILE_MARGIN_PX)))
        rows = max(1, int(available_height_px // (TILE_HEIGHT_PX + TILE_MARGIN_PX)))
        per_page = rows * cols
        
        print(f"Tile layout: {cols} columns x {rows} rows = {per_page} SVGs per page")
    
    # Create the root SVG element
    # Note: namespaces are declared via nsmap, not as attributes
    root = etree.Element(
        f"{{{SVG_NS}}}svg",
        attrib={
            "width": f"{PAGE_WIDTH}in",
            "height": f"{PAGE_HEIGHT}in",
            "viewBox": f"0 0 {PAGE_WIDTH_PX} {PAGE_HEIGHT_PX}",
            "version": "1.1",
        },
        nsmap={
            None: SVG_NS,
            'inkscape': INKSCAPE_NS,
            'sodipodi': SODIPODI_NS,
        }
    )
    
    # Add defs section (required for proper Inkscape structure)
    defs = etree.SubElement(root, f"{{{SVG_NS}}}defs")
    
    # Add Inkscape-specific namedview for document settings
    namedview = etree.SubElement(
        root,
        f"{{{SODIPODI_NS}}}namedview",
        attrib={
            "pagecolor": "#ffffff",
            "bordercolor": "#666666",
            "borderopacity": "1.0",
            f"{{{INKSCAPE_NS}}}document-units": "in",
            f"{{{INKSCAPE_NS}}}current-layer": "page_1",
            "showgrid": "false",
        }
    )
    
    # Sort groups alphabetically
    sorted_groups = sorted(svg_groups.keys(), key=natural_sort_key)
    
    page_num = 1
    total_pages = 0
    
    if mode == "stack":
        # Original stack mode
        for group_name in sorted_groups:
            svg_files = svg_groups[group_name]
            
            print(f"\nProcessing page {page_num}: {group_name}")
            print(f"  Adding {len(svg_files)} layers...")
            
            # Calculate Y offset for this page (pages stack vertically)
            page_y_offset = (page_num - 1) * (PAGE_HEIGHT_PX + 100)  # 100px gap between pages
            
            # Create an Inkscape page element
            page_element = etree.SubElement(
                namedview,
                f"{{{INKSCAPE_NS}}}page",
                attrib={
                    "x": "0",
                    "y": str(page_y_offset),
                    "width": str(PAGE_WIDTH_PX),
                    "height": str(PAGE_HEIGHT_PX),
                    "id": f"page_{page_num}",
                    f"{{{INKSCAPE_NS}}}label": f"{group_name}",
                }
            )
            
            # Create a group to hold all layers for this page
            page_group = etree.SubElement(
                root,
                f"{{{SVG_NS}}}g",
                attrib={
                    f"{{{INKSCAPE_NS}}}groupmode": "layer",
                    f"{{{INKSCAPE_NS}}}label": f"Page {page_num}: {group_name}",
                    "id": f"page_group_{page_num}",
                    "transform": f"translate(0, {page_y_offset})",
                }
            )
            
            # Add each SVG file as a layer within this page group
            for idx, svg_file in enumerate(svg_files, 1):
                layer_name = f"{svg_file.stem}"  # Filename without extension
                print(f"    - {layer_name}")

                layer = create_centered_layer(svg_file, layer_name, page_num, idx)
                if layer is not None:
                    page_group.append(layer)
            
            page_num += 1
        
        total_pages = page_num - 1
    
    elif mode == "tile":
        # Tile mode: all SVGs in one group, tiled across pages
        all_svgs = svg_groups["All_SVGs"]
        total_svgs = len(all_svgs)
        
        for page_start in range(0, total_svgs, per_page):
            page_svgs = all_svgs[page_start:page_start + per_page]
            
            print(f"\nProcessing page {page_num}: SVGs {page_start + 1} to {page_start + len(page_svgs)}")
            
            # Calculate Y offset for this page
            page_y_offset = (page_num - 1) * (PAGE_HEIGHT_PX + 100)
            
            # Create an Inkscape page element
            page_element = etree.SubElement(
                namedview,
                f"{{{INKSCAPE_NS}}}page",
                attrib={
                    "x": "0",
                    "y": str(page_y_offset),
                    "width": str(PAGE_WIDTH_PX),
                    "height": str(PAGE_HEIGHT_PX),
                    "id": f"page_{page_num}",
                    f"{{{INKSCAPE_NS}}}label": f"Page {page_num}",
                }
            )
            
            # Create a group to hold all layers for this page
            page_group = etree.SubElement(
                root,
                f"{{{SVG_NS}}}g",
                attrib={
                    f"{{{INKSCAPE_NS}}}groupmode": "layer",
                    f"{{{INKSCAPE_NS}}}label": f"Page {page_num}",
                    "id": f"page_group_{page_num}",
                    "transform": f"translate(0, {page_y_offset})",
                }
            )
            
            # Add each SVG file as a tiled layer
            for idx, svg_file in enumerate(page_svgs):
                layer_name = f"{svg_file.stem}"
                print(f"    - {layer_name}")
                
                # Calculate grid position
                col = idx % cols
                row = idx // cols
                
                # Calculate position in pixels
                x = TILE_MARGIN_PX + col * (TILE_WIDTH_PX + TILE_MARGIN_PX)
                y = TILE_MARGIN_PX + row * (TILE_HEIGHT_PX + TILE_MARGIN_PX)
                
                # Get SVG dimensions and calculate scale
                svg_width, svg_height = get_svg_viewbox(svg_file)
                if svg_width > 0 and svg_height > 0:
                    scale_x = TILE_WIDTH_PX / svg_width
                    scale_y = TILE_HEIGHT_PX / svg_height
                    scale = min(scale_x, scale_y)
                else:
                    scale = 1.0
                
                # Center within the tile
                scaled_width = svg_width * scale
                scaled_height = svg_height * scale
                offset_x = (TILE_WIDTH_PX - scaled_width) / 2
                offset_y = (TILE_HEIGHT_PX - scaled_height) / 2
                
                final_x = x + offset_x
                final_y = y + offset_y
                
                layer = create_tiled_layer(svg_file, layer_name, final_x, final_y, scale)
                if layer is not None:
                    page_group.append(layer)
            
            page_num += 1
        
        total_pages = page_num - 1
    
    # Update the root SVG height to accommodate all pages
    total_height = total_pages * (PAGE_HEIGHT_PX + 100) - 100  # Subtract extra gap
    root.set("height", f"{total_height / DPI}in")
    root.set("viewBox", f"0 0 {PAGE_WIDTH_PX} {total_height}")
    
    # Write the combined SVG
    tree = etree.ElementTree(root)
    tree.write(
        str(output_path),
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8'
    )
    
    print(f"\n✓ Successfully created {output_path}")
    print(f"  Total pages: {total_pages}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main function - handles user input and orchestrates the combination process
    """
    print("=" * 70)
    print("SVG Multi-Page Combiner")
    print("=" * 70)
    print()
    
    # Get the root directory from user
    if len(sys.argv) > 1:
        # If a path was provided as command line argument
        root_dir = sys.argv[1]
    else:
        # Ask the user for the path
        root_dir = input("Enter the root folder path containing your SVG files:\n> ").strip()
        
        # Remove quotes if user copied path from Windows Explorer
        root_dir = root_dir.strip('"').strip("'")
    
    root_path = Path(root_dir)
    
    # Validate the path
    if not root_path.exists():
        print(f"\n✗ Error: Path does not exist: {root_path}")
        input("\nPress Enter to exit...")
        return
    
    if not root_path.is_dir():
        print(f"\n✗ Error: Path is not a directory: {root_path}")
        input("\nPress Enter to exit...")
        return
    
    print(f"\nScanning directory: {root_path}")
    print("=" * 70)
    
    # Find all SVG files based on mode
    svg_groups = find_all_svgs(root_path, MODE)
    
    if not svg_groups:
        print("\n✗ No SVG files found in any subdirectories!")
        input("\nPress Enter to exit...")
        return
    
    total_svgs = sum(len(files) for files in svg_groups.values())
    if MODE == "stack":
        print(f"\n Found {len(svg_groups)} parent folders with SVG files")
    else:
        print(f"\n Found {total_svgs} SVG files total")
    print(f"Total SVG files to process: {total_svgs}")
    
    # Determine output filename
    if OUTPUT_FILENAME == "ASK":
        print("\n" + "=" * 70)
        filename = input("Enter output filename (without path): ").strip()
        if not filename.endswith('.svg'):
            filename += '.svg'
    elif OUTPUT_FILENAME is None:
        # Use root folder name + "_ALL.svg"
        folder_name = root_path.name
        filename = f"{folder_name}_ALL.svg"
        print(f"\nOutput filename: {filename}")
    else:
        filename = OUTPUT_FILENAME
    
    # Confirm before processing
    print("\n" + "=" * 70)
    mode_desc = "stacked as layers" if MODE == "stack" else "tiled on pages"
    response = input(f"\nCreate '{filename}' with {total_svgs} SVGs {mode_desc}? (y/n): ").strip().lower()
    
    if response != 'y':
        print("\nOperation cancelled.")
        input("\nPress Enter to exit...")
        return
    
    # Create the output file
    output_path = root_path / filename
    
    print("\n" + "=" * 70)
    print("Processing files...")
    print("=" * 70)
    
    try:
        create_multipage_svg(svg_groups, output_path, MODE)
        
        print("\n" + "=" * 70)
        print("✓ DONE!")
        print("=" * 70)
        print(f"\nYour combined SVG file is ready:")
        print(f"  {output_path}")
        if MODE == "stack":
            print(f"\nOpen it in Inkscape to see all {len(svg_groups)} pages.")
        else:
            print(f"\nOpen it in Inkscape to see all tiled SVGs across pages.")
        
    except Exception as e:
        print(f"\n✗ Error creating SVG file: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
