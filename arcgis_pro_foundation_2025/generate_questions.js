/**
 * Generate additional EAPF 2025 questions (q31–q210). Run: node generate_questions.js
 * Output: appends to questions.json (run from this directory).
 */
const fs = require('fs');

const TEMPLATES = [
  ["data-management", "Which geodatabase type is stored as a folder on disk?", ["File geodatabase", "Enterprise geodatabase only", "Shapefile", "CSV"], 0],
  ["data-management", "What must you do before editing features in ArcGIS Pro?", ["Start an edit session", "Export the layer", "Change symbology", "Add a layout"], 0],
  ["data-management", "Which property prevents a field from containing null values?", ["Nullable", "Length", "Alias", "Default value"], 0],
  ["data-management", "A shapefile can store which geometry type?", ["Points, lines, or polygons", "Only rasters", "Only annotations", "Only tables"], 0],
  ["data-management", "Where is the default geodatabase for a project set?", ["Project properties", "Map properties only", "Layout view", "Symbology pane"], 0],
  ["data-management", "What does saving edits do in an edit session?", ["Commits changes to the data", "Exports the map", "Creates a backup", "Changes symbology"], 0],
  ["data-management", "Which format is a single file that can hold multiple feature classes?", ["File geodatabase", "Shapefile", "CSV", "TXT"], 0],
  ["data-management", "To add a new field to an existing attribute table, you use:", ["Add Field or Fields view", "Symbology pane only", "Layout view", "Map properties only"], 0],
  ["data-management", "A projected coordinate system is often used to:", ["Measure distances and areas in consistent units", "Store metadata only", "Display labels only", "Export to PDF"], 0],
  ["data-management", "Which data format stores one feature class per file and has .shp, .shx, .dbf?", ["Shapefile", "File geodatabase", "CSV", "Raster"], 0],
  ["mapping-visualization", "The ribbon in ArcGIS Pro contains:", ["Contextual tabs and tools for the active view", "Only the map", "Only the layout", "Only metadata"], 0],
  ["mapping-visualization", "Which symbology shows quantities with symbol size?", ["Proportional symbols", "Unique values", "Graduated colors", "Single symbol"], 0],
  ["mapping-visualization", "The Contents pane shows:", ["Layers, their order, and visibility", "Only the Catalog", "Only geoprocessing history", "Only attributes"], 0],
  ["mapping-visualization", "To change the order of layers on the map, you:", ["Drag layers in the Contents pane", "Use the Catalog pane only", "Change the coordinate system", "Export to PDF"], 0],
  ["mapping-visualization", "A reference scale is used to:", ["Fix symbol and text sizes at a specific scale", "Add new layers", "Run geoprocessing", "Edit attributes"], 0],
  ["layouts-sharing", "To share a map so others can open it in ArcGIS Pro with data, you can create:", ["A map package (.mpkx)", "A CSV file only", "A shapefile only", "A text file only"], 0],
  ["layouts-sharing", "Exporting a layout to PDF produces:", ["A static document for printing or sharing", "An editable project", "A geodatabase", "A feature class"], 0],
  ["performing-analysis", "The Buffer tool creates:", ["Polygons at a distance from input features", "New attribute fields only", "New maps only", "New layouts only"], 0],
  ["performing-analysis", "To select features that intersect another layer, you use:", ["Select By Location", "Select By Attributes only", "Calculate Field only", "Symbology only"], 0],
  ["performing-analysis", "The Clip tool:", ["Extracts features that fall within a clip boundary", "Merges two layers", "Creates buffers", "Adds fields"], 0],
  ["performing-analysis", "To find features where an attribute equals a value, you use:", ["Select By Attributes", "Select By Location only", "Buffer only", "Clip only"], 0],
  ["performing-analysis", "The Merge tool:", ["Combines multiple feature classes into one", "Clips features", "Creates buffers", "Calculates area only"], 0],
  ["data-management", "Editing in ArcGIS Pro applies to:", ["The data source", "A copy in memory only", "The layout only", "Metadata only"], 0],
  ["data-management", "Which field type stores calendar dates?", ["Date", "Integer", "Float", "Text"], 0],
  ["data-management", "The spatial reference of a layer includes:", ["Coordinate system and coordinate extent", "Symbology only", "Labels only", "Layout size"], 0],
  ["data-management", "To discard edits without saving, you:", ["Stop editing and choose not to save", "Save the project", "Export the layer", "Change the coordinate system"], 0],
  ["data-management", "A feature class can contain:", ["One geometry type (point, line, or polygon)", "Mixed geometry types", "Only tables", "Only rasters"], 0],
  ["data-management", "Which pane do you use to create a new file geodatabase?", ["Catalog pane", "Contents pane only", "Layout view", "Symbology pane"], 0],
  ["mapping-visualization", "Which view do you use to design a printable map with title and legend?", ["Layout view", "Map view only", "Catalog pane", "Geoprocessing pane"], 0],
  ["mapping-visualization", "Labels are typically based on:", ["A field in the attribute table", "The coordinate system only", "The map extent only", "Symbology only"], 0],
  ["mapping-visualization", "To show only features that meet a condition, you can use:", ["A definition query", "Only symbology", "Only the coordinate system", "Only the layout"], 0],
  ["mapping-visualization", "Bookmarks in ArcGIS Pro store:", ["Named map extents for quick navigation", "Only layer order", "Only symbology", "Only attribute values"], 0],
  ["mapping-visualization", "The basemap is usually:", ["A background layer (e.g., imagery or streets)", "The top layer", "A table", "A layout element"], 0],
  ["mapping-visualization", "Which symbology method assigns one symbol per category?", ["Unique values", "Graduated colors", "Heat map", "Proportional symbols"], 0],
  ["mapping-visualization", "To add data from your computer, you typically use:", ["Catalog pane or Add Data", "Layout view only", "Symbology pane only", "Geoprocessing only"], 0],
  ["mapping-visualization", "A map frame on a layout:", ["Displays a map view and can be linked to a map", "Stores attributes only", "Runs geoprocessing", "Edits metadata"], 0],
  ["mapping-visualization", "Layer visibility (eye icon) in the Contents pane:", ["Turns drawing of the layer on or off", "Deletes the layer", "Exports the layer", "Changes the coordinate system"], 0],
  ["mapping-visualization", "Which pane lists project items such as maps, folders, and databases?", ["Catalog pane", "Contents pane only", "Attributes pane only", "Layout view"], 0],
  ["mapping-visualization", "The attribute table of a layer shows:", ["Rows (features) and columns (fields)", "Only the map extent", "Only symbology", "Only the layout"], 0],
  ["layouts-sharing", "A layer package includes:", ["The layer and its data", "Only the symbology", "Only the coordinate system", "Only the layout"], 0],
  ["layouts-sharing", "To share a project with its maps and data, you can use:", ["A project package (.ppkx)", "A single shapefile", "A CSV only", "A text file only"], 0],
  ["layouts-sharing", "When you share a web layer to a portal, others can:", ["Add it to their maps in ArcGIS Online or Pro", "Only open it in one project", "Only view metadata", "Only edit the source data"], 0],
  ["performing-analysis", "Geoprocessing tools can be run from:", ["The Geoprocessing pane or Catalog pane", "The Symbology pane only", "The Layout view only", "The Attributes pane only"], 0],
  ["performing-analysis", "To create a new layer from selected features, you can:", ["Right-click the layer and use Selection > Create Layer", "Only change symbology", "Only export to PDF", "Only change the coordinate system"], 0],
  ["performing-analysis", "The Intersect tool finds:", ["Areas where input features overlap", "Only the extent of the map", "Only attribute values", "Only labels"], 0],
  ["performing-analysis", "Search in the Geoprocessing pane helps you:", ["Find tools by name or keyword", "Add layers only", "Change symbology only", "Edit metadata only"], 0],
  ["performing-analysis", "To clear the current selection, you use:", ["Clear selection (e.g., from Map or layer context menu)", "Save the project", "Export the layer", "Change the layout"], 0],
];

function shuffle(a) {
  const arr = a.slice();
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

const out = [];
for (let i = 0; i < 180; i++) {
  const idx = 31 + i;
  const t = TEMPLATES[i % TEMPLATES.length];
  const domain = t[0];
  const text = t[1];
  let opts = t[2].slice();
  const correctIdx = t[3] !== undefined ? t[3] : 0;
  const correctVal = opts[correctIdx];
  opts = shuffle(opts);
  const newIdx = opts.indexOf(correctVal);
  const keys = ['a', 'b', 'c', 'd'];
  const optionJson = keys.map((k, j) => ({ key: k, text: opts[j] }));
  out.push({
    id: 'q' + String(idx).padStart(2, '0'),
    domainId: domain,
    text: text,
    options: optionJson,
    correctKey: keys[newIdx]
  });
}

const path = require('path');
const questionsPath = path.join(__dirname, 'questions.json');
const data = JSON.parse(fs.readFileSync(questionsPath, 'utf8'));
data.questions = data.questions.concat(out);
fs.writeFileSync(questionsPath, JSON.stringify(data, null, 2), 'utf8');
