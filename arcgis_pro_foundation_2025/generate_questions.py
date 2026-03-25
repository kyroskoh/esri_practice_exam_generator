#!/usr/bin/env python3
"""
Generate additional EAPF 2025 practice questions. Aligns to EIG domains.

Default: 100 questions, start auto-detected from questions.json.

  python generate_questions.py
    → 100 questions (start auto-detected; print to stdout)
  python generate_questions.py > new_questions.json 2>&1 && python generate_questions_cursor.py merge new_questions.json
    → default: generate 100, then merge
  python generate_questions.py --count 50
    → 50 questions; use --start N to override start id
"""
import argparse
import json
import os
import random

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_PATH = os.path.join(SCRIPT_DIR, "questions.json")

DOMAINS = [
    "data-management",      # 32%
    "mapping-visualization", # 36%
    "layouts-sharing",       # 12%
    "performing-analysis",  # 20%
]

# Question templates: (domain_id, text, options_list, correct_index 0-3)
# Options are [correct, wrong1, wrong2, wrong3]; we shuffle when emitting
TEMPLATES = [
    # Data Management
    ("data-management", "Which geodatabase type is stored as a folder on disk?", ["File geodatabase", "Enterprise geodatabase only", "Shapefile", "CSV"], 0),
    ("data-management", "What must you do before editing features in ArcGIS Pro?", ["Start an edit session", "Export the layer", "Change symbology", "Add a layout"], 0),
    ("data-management", "Which property prevents a field from containing null values?", ["Nullable", "Length", "Alias", "Default value"], 0),
    ("data-management", "A shapefile can store which geometry type?", ["Points, lines, or polygons", "Only rasters", "Only annotations", "Only tables"], 0),
    ("data-management", "Where is the default geodatabase for a project set?", ["Project properties", "Map properties only", "Layout view", "Symbology pane"]),
    ("data-management", "What does saving edits do in an edit session?", ["Commits changes to the data", "Exports the map", "Creates a backup", "Changes symbology"]),
    ("data-management", "Which format is a single file that can hold multiple feature classes?", ["File geodatabase", "Shapefile", "CSV", "TXT"]),
    ("data-management", "To add a new field to an existing attribute table, you use:", ["Add Field or Fields view", "Symbology pane only", "Layout view", "Map properties only"]),
    ("data-management", "A projected coordinate system is often used to:", ["Measure distances and areas in consistent units", "Store metadata only", "Display labels only", "Export to PDF"]),
    ("data-management", "Which data format stores one feature class per file and has .shp, .shx, .dbf?", ["Shapefile", "File geodatabase", "CSV", "Raster"]),
    ("data-management", "Editing in ArcGIS Pro applies to:", ["The data source", "A copy in memory only", "The layout only", "Metadata only"]),
    ("data-management", "Which field type stores calendar dates?", ["Date", "Integer", "Float", "Text"]),
    ("data-management", "The spatial reference of a layer includes:", ["Coordinate system and coordinate extent", "Symbology only", "Labels only", "Layout size"]),
    ("data-management", "To discard edits without saving, you:", ["Stop editing and choose not to save", "Save the project", "Export the layer", "Change the coordinate system"]),
    ("data-management", "A feature class can contain:", ["One geometry type (point, line, or polygon)", "Mixed geometry types", "Only tables", "Only rasters"]),
    ("data-management", "Which pane do you use to create a new file geodatabase?", ["Catalog pane", "Contents pane only", "Layout view", "Symbology pane"]),
    ("data-management", "Attribute domains can be used to:", ["Constrain allowed values for a field", "Change symbology", "Add a layout", "Export to PDF"]),
    ("data-management", "The alias of a field is:", ["A display name that can differ from the field name", "The coordinate system", "The data type", "The default value"]),
    ("data-management", "Which key do you press to delete a selected feature during editing?", ["Delete or Backspace", "Enter only", "Escape only", "Tab only"]),
    ("data-management", "A table that has a spatial column can be displayed as:", ["A layer (e.g., XY Table To Point)", "Only in the Catalog", "Only in a layout", "Only as metadata"]),
    # Mapping and Visualization
    ("mapping-visualization", "The ribbon in ArcGIS Pro contains:", ["Contextual tabs and tools for the active view", "Only the map", "Only the layout", "Only metadata"]),
    ("mapping-visualization", "Which symbology shows quantities with symbol size?", ["Proportional symbols", "Unique values", "Graduated colors", "Single symbol"]),
    ("mapping-visualization", "The Contents pane shows:", ["Layers, their order, and visibility", "Only the Catalog", "Only geoprocessing history", "Only attributes"]),
    ("mapping-visualization", "To change the order of layers on the map, you:", ["Drag layers in the Contents pane", "Use the Catalog pane only", "Change the coordinate system", "Export to PDF"]),
    ("mapping-visualization", "A reference scale is used to:", ["Fix symbol and text sizes at a specific scale", "Add new layers", "Run geoprocessing", "Edit attributes"]),
    ("mapping-visualization", "Which view do you use to design a printable map with title and legend?", ["Layout view", "Map view only", "Catalog pane", "Geoprocessing pane"]),
    ("mapping-visualization", "Labels are typically based on:", ["A field in the attribute table", "The coordinate system only", "The map extent only", "Symbology only"]),
    ("mapping-visualization", "The Map tab on the ribbon appears when:", ["A map or scene is active", "The Catalog is active", "A layout is active", "Metadata is open"]),
    ("mapping-visualization", "To show only features that meet a condition, you can use:", ["A definition query", "Only symbology", "Only the coordinate system", "Only the layout"]),
    ("mapping-visualization", "Bookmarks in ArcGIS Pro store:", ["Named map extents for quick navigation", "Only layer order", "Only symbology", "Only attribute values"]),
    ("mapping-visualization", "The basemap is usually:", ["A background layer (e.g., imagery or streets)", "The top layer", "A table", "A layout element"]),
    ("mapping-visualization", "Which symbology method assigns one symbol per category?", ["Unique values", "Graduated colors", "Heat map", "Proportional symbols"]),
    ("mapping-visualization", "The Quick Access Toolbar allows you to:", ["Add frequently used commands", "Store layers only", "Change coordinate system only", "Run Python only"]),
    ("mapping-visualization", "To add data from your computer, you typically use:", ["Catalog pane or Add Data", "Layout view only", "Symbology pane only", "Geoprocessing only"]),
    ("mapping-visualization", "A map frame on a layout:", ["Displays a map view and can be linked to a map", "Stores attributes only", "Runs geoprocessing", "Edits metadata"]),
    ("mapping-visualization", "Layer visibility (eye icon) in the Contents pane:", ["Turns drawing of the layer on or off", "Deletes the layer", "Exports the layer", "Changes the coordinate system"]),
    ("mapping-visualization", "Which pane lists project items such as maps, folders, and databases?", ["Catalog pane", "Contents pane only", "Attributes pane only", "Layout view"]),
    ("mapping-visualization", "The attribute table of a layer shows:", ["Rows (features) and columns (fields)", "Only the map extent", "Only symbology", "Only the layout"]),
    ("mapping-visualization", "To zoom to the full extent of all layers, you use:", ["Full Extent button or right-click", "Catalog pane only", "Metadata only", "Layout view only"]),
    ("mapping-visualization", "A layout can include:", ["Map frame(s), legend, scale bar, title, north arrow", "Only attribute tables", "Only geoprocessing tools", "Only the Catalog"]),
    # Layouts and Sharing
    ("layouts-sharing", "To share a map so others can open it in ArcGIS Pro with data, you can create:", ["A map package (.mpkx)", "A CSV file only", "A shapefile only", "A text file only"]),
    ("layouts-sharing", "Exporting a layout to PDF produces:", ["A static document for printing or sharing", "An editable project", "A geodatabase", "A feature class"]),
    ("layouts-sharing", "A layer package includes:", ["The layer and its data", "Only the symbology", "Only the coordinate system", "Only the layout"]),
    ("layouts-sharing", "To share a project with its maps and data, you can use:", ["A project package (.ppkx)", "A single shapefile", "A CSV only", "A text file only"]),
    ("layouts-sharing", "Which format is suitable for printing a single map?", ["PDF or other export from Layout", "Project file only", "Geodatabase only", "Feature class only"]),
    ("layouts-sharing", "When you share a web layer to a portal, others can:", ["Add it to their maps in ArcGIS Online or Pro", "Only open it in one project", "Only view metadata", "Only edit the source data"]),
    ("layouts-sharing", "The Share menu in ArcGIS Pro can be used to:", ["Package or share maps and layers", "Run geoprocessing only", "Edit attributes only", "Change symbology only"]),
    ("layouts-sharing", "A map package is different from a project package in that:", ["It contains a map and its data, not the full project", "It contains only layouts", "It contains only Python scripts", "It contains only metadata"]),
    ("layouts-sharing", "To allow someone without ArcGIS to view your map, you could:", ["Export the layout to PDF", "Share only the project file", "Share only the geodatabase", "Share only a CSV"]),
    ("layouts-sharing", "Publishing a feature layer to a portal makes it:", ["Available as a web layer for others to use", "Only visible in your project", "Only in the Catalog", "Only in the layout"]),
    # Performing Analysis
    ("performing-analysis", "The Buffer tool creates:", ["Polygons at a distance from input features", "New attribute fields only", "New maps only", "New layouts only"]),
    ("performing-analysis", "To select features that intersect another layer, you use:", ["Select By Location", "Select By Attributes only", "Calculate Field only", "Symbology only"]),
    ("performing-analysis", "The Clip tool:", ["Extracts features that fall within a clip boundary", "Merges two layers", "Creates buffers", "Adds fields"]),
    ("performing-analysis", "To find features where an attribute equals a value, you use:", ["Select By Attributes", "Select By Location only", "Buffer only", "Clip only"]),
    ("performing-analysis", "The Merge tool:", ["Combines multiple feature classes into one", "Clips features", "Creates buffers", "Calculates area only"]),
    ("performing-analysis", "Geoprocessing tools can be run from:", ["The Geoprocessing pane or Catalog pane", "The Symbology pane only", "The Layout view only", "The Attributes pane only"]),
    ("performing-analysis", "To create a new layer from selected features, you can:", ["Right-click the layer and use Selection > Create Layer", "Only change symbology", "Only export to PDF", "Only change the coordinate system"]),
    ("performing-analysis", "The Intersect tool finds:", ["Areas where input features overlap", "Only the extent of the map", "Only attribute values", "Only labels"]),
    ("performing-analysis", "Search in the Geoprocessing pane helps you:", ["Find tools by name or keyword", "Add layers only", "Change symbology only", "Edit metadata only"]),
    ("performing-analysis", "To clear the current selection, you use:", ["Clear selection (e.g., from Map or layer context menu)", "Save the project", "Export the layer", "Change the layout"]),
    # Extra templates for 100 more questions (q201–q300)
    ("data-management", "To create a new project from a template, you:", ["Use the start page or File > New and choose a template", "Run Buffer only", "Export to CSV only", "Change symbology only"]),
    ("data-management", "The Geoprocessing History pane shows:", ["Tools you have run in the project", "Only the map extent", "Only symbology", "Only the layout"]),
    ("data-management", "Which field property limits character length for text?", ["Length", "Alias", "Nullable", "Default value"]),
    ("data-management", "A relationship class links:", ["Two tables or feature classes by a key field", "Only maps and layouts", "Only rasters", "Only CSV files"]),
    ("data-management", "To export a feature class to a new geodatabase, you use:", ["Feature Class To Feature Class or Copy", "Symbology pane only", "Layout view only", "Buffer only"]),
    ("data-management", "Versioning in a geodatabase is used for:", ["Multiuser editing and reconciliation", "Symbology only", "Layout only", "Export to PDF only"]),
    ("data-management", "The schema of a feature class defines:", ["Fields, geometry type, and spatial reference", "Only colors", "Only labels", "Only the map extent"]),
    ("data-management", "To repair broken data sources in a map, you:", ["Right-click the layer and choose Data > Repair Data Source", "Run Buffer only", "Export to CSV only", "Change symbology only"]),
    ("data-management", "A stand-alone table in a geodatabase:", ["Has no geometry; stores attribute rows only", "Is always a raster", "Is always a layout", "Cannot be opened"]),
    ("data-management", "Which coordinate system unit is typical for a projected system?", ["Meters or feet", "Degrees only", "Pixels only", "Miles per hour"]),
    ("mapping-visualization", "To show a different symbol for selected features, you set:", ["Selection symbology in the layer properties or Symbology pane", "Coordinate system only", "Layout only", "Buffer tool only"]),
    ("mapping-visualization", "The Format tab for a map frame appears when:", ["A map frame is selected on the layout", "The Catalog is active", "A table is open", "Geoprocessing runs"]),
    ("mapping-visualization", "To align a map frame to the edge of the layout, you use:", ["Format tab Align or Distribute options", "Geoprocessing only", "Catalog pane only", "Attributes pane only"]),
    ("mapping-visualization", "A scale bar on a layout:", ["Shows the relationship between map and ground distance", "Stores attributes only", "Runs geoprocessing", "Edits metadata"]),
    ("mapping-visualization", "To lock the aspect ratio of a map frame, you:", ["Use the map frame properties or Format tab", "Run Buffer only", "Export to CSV only", "Change coordinate system only"]),
    ("mapping-visualization", "The Explore tool is used to:", ["Pan and click to identify or open pop-ups", "Run Buffer only", "Edit attributes only", "Export to PDF only"]),
    ("mapping-visualization", "Layer transparency is set in:", ["Layer properties or the Appearance tab", "Catalog pane only", "Geoprocessing only", "Layout view only"]),
    ("mapping-visualization", "A north arrow on a layout:", ["Indicates map orientation", "Stores attributes", "Runs analysis", "Exports data"]),
    ("layouts-sharing", "To allow others to edit a shared feature layer, you:", ["Share as a feature layer with edit capability enabled", "Export to CSV only", "Run Buffer only", "Change symbology only"]),
    ("layouts-sharing", "A tile package is used to:", ["Share basemap or cached tiles for offline use", "Store only attributes", "Run geoprocessing only", "Edit metadata only"]),
    ("layouts-sharing", "When you package a project, you can:", ["Include maps, data, and toolboxes", "Include only the layout", "Include only symbology", "Include only the Catalog"]),
    ("layouts-sharing", "Sharing a web map to a portal allows others to:", ["View and optionally edit in a browser or app", "Only open in one project", "Only run Buffer", "Only change coordinate system"]),
    ("layouts-sharing", "The Share As Web Map pane is used to:", ["Publish a map to ArcGIS Online or a portal", "Run Buffer only", "Edit attributes only", "Change symbology only"]),
    ("layouts-sharing", "A vector tile package (.vtpk) is used for:", ["Stylized basemap layers", "Storing only attribute tables", "Running geoprocessing", "Editing features only"]),
    ("layouts-sharing", "To overwrite an existing web layer, you:", ["Choose Overwrite when sharing", "Export to CSV only", "Run Buffer only", "Change layout only"]),
    ("performing-analysis", "The Trace Downstream tool:", ["Traces the path downstream from points in a flow direction raster", "Creates buffers only", "Selects by attributes only", "Exports to PDF only"]),
    ("performing-analysis", "The Find Similar Locations tool:", ["Finds places that match criteria based on attributes and optionally location", "Creates buffers only", "Clips features only", "Exports to PDF only"]),
    ("performing-analysis", "To summarize attributes of features within zones, you might use:", ["Summarize Within or Summary Statistics", "Buffer only", "Clip only", "Symbology only"]),
    ("performing-analysis", "The Near tool:", ["Calculates distance from each input feature to the nearest feature in another layer", "Merges layers only", "Creates buffers only", "Exports to PDF only"]),
    ("performing-analysis", "To combine two polygon layers and keep overlapping areas only, you use:", ["Intersect", "Buffer only", "Merge only", "Clip only"]),
    ("performing-analysis", "The Union tool:", ["Combines features from two layers and splits overlapping areas", "Creates buffers only", "Selects by attributes only", "Exports to PDF only"]),
    ("performing-analysis", "To find the area of overlap between two polygon layers, you can use:", ["Intersect or Union", "Buffer only", "Symbology only", "Layout only"]),
    ("performing-analysis", "The Spatial Join tool:", ["Joins attributes from one layer to another based on location", "Merges only", "Clips only", "Exports only"]),
    ("performing-analysis", "To place points from a table with address column, you use:", ["Geocoding or Locate", "Buffer only", "Clip only", "Symbology only"]),
]


def _detect_start():
    """Return (current question count + 1) from questions.json, or 1 if not found/invalid."""
    if not os.path.isfile(QUESTIONS_PATH):
        return 1
    try:
        with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        questions = data.get("questions", [])
        return len(questions) + 1
    except (json.JSONDecodeError, OSError):
        return 1


def main():
    parser = argparse.ArgumentParser(description="Generate EAPF 2025 practice questions.")
    parser.add_argument(
        "--start", type=int, default=None, metavar="N",
        help="First question number (e.g. 201). If omitted, auto-detect from questions.json in this folder (current count + 1)."
    )
    parser.add_argument("--count", type=int, default=100, help="Number of questions to generate (default: 100)")
    args = parser.parse_args()
    start = args.start if args.start is not None else _detect_start()
    random.seed(42)
    out = []
    for i in range(args.count):
        idx = start + i
        t = random.choice(TEMPLATES)
        if len(t) == 5:
            domain, text, opts, correct_idx = t[0], t[1], t[2], t[3]
        else:
            domain, text, opts = t[0], t[1], t[2]
            correct_idx = 0
        if len(opts) != 4:
            opts = (opts + ["None of the above"] * 4)[:4]
        correct_val = opts[correct_idx]
        opts_shuffled = opts.copy()
        random.shuffle(opts_shuffled)
        new_idx = opts_shuffled.index(correct_val)
        keys = ["a", "b", "c", "d"]
        correct_key = keys[new_idx]
        option_json = [{"key": k, "text": opts_shuffled[j]} for j, k in enumerate(keys)]
        id_fmt = "q{:d}" if idx >= 100 else "q{:02d}"
        out.append({
            "id": id_fmt.format(idx),
            "domainId": domain,
            "text": text,
            "options": option_json,
            "correctKey": correct_key
        })
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
