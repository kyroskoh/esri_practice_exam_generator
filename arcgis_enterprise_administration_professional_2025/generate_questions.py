#!/usr/bin/env python3
"""
Generate additional EAEP 2025 practice questions from **fixed templates** (short factual stems).

This path is **not** the same as the **case-study / best-answer** bank used for exam-like
scenarios. For those, use:
  - `build_eaep_scenario_bank.py` (rebuilds questions.json with CertFun + scenario items), and/or
  - `generate_questions_cursor.py prompt` (prompt tuned for tricky scenarios in
    `prompt_for_cursor_questions.txt`).

`emit_bulk_questions.py` combines **intro phrases** with these same templates to add volume;
merge output is still template-style, not full case studies.

Templates below align to EIG **domains**; difficulty is drill-level. Original stems only
(not copied from third-party sample banks).

  python generate_questions.py
  python generate_questions.py > new_questions.json 2>&1 && python generate_questions_cursor.py merge new_questions.json
"""
import argparse
import json
import os
import random

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_PATH = os.path.join(SCRIPT_DIR, "questions.json")


def q(domain, text, correct, w1, w2, w3):
    return (domain, text, [correct, w1, w2, w3], 0)


# Template drills — factual / single-sentence style. For scenario stems, extend via
# build_eaep_scenario_bank.py (SCENARIO_SPECS) or Cursor merge, not by mixing styles here.
# (domain, text, options[correct,...wrong], correct_index=0)
TEMPLATES = [
    # Deploy ArcGIS Enterprise (~34%)
    q("deploy-enterprise", "Which ArcGIS Data Store type primarily supports hosted feature layers and scene layer caches in a base deployment?", "Relational data store", "Tile cache data store only", "Graph store only", "Spatiotemporal big data store only"),
    q("deploy-enterprise", "Which component serves as the identity and sharing hub in a standard ArcGIS Enterprise base deployment?", "Portal for ArcGIS", "ArcGIS Server only", "ArcGIS Web Adaptor only", "ArcGIS Monitor only"),
    q("deploy-enterprise", "What is the primary role of ArcGIS Web Adaptor in a typical on-premises deployment?", "Expose ArcGIS Server and Portal through your organization's web server URL", "Replace the need for Portal for ArcGIS", "Host the relational data store database", "License ArcGIS Desktop clients"),
    q("deploy-enterprise", "Before users can publish hosted layers through the portal, which ArcGIS Server role must typically be assigned to the federated server?", "Hosting server", "Raster analytics server only", "Image hosting server only", "GeoAnalytics server only"),
    q("deploy-enterprise", "Which file is used to provision user types and add-on licenses in an ArcGIS Enterprise deployment?", "ArcGIS Enterprise authorization file (.json)", "A .prvc file only", "A shapefile .prj file", "An .mxd map document"),
    q("deploy-enterprise", "Which practice helps browsers trust HTTPS connections to your portal site in production?", "Bind a certificate from a public or organizational CA to the endpoint users reach", "Use only self-signed certificates without distribution", "Disable TLS on the Web Adaptor", "Share the portal over HTTP only"),
    q("deploy-enterprise", "Which ArcGIS Data Store type is used for tile layer caches when publishing hosted tile layers?", "Tile cache data store", "Relational data store only", "Object store only", "File geodatabase"),
    q("deploy-enterprise", "When federating ArcGIS Server with the portal, where is the server URL that clients should use typically exposed?", "Through the Web Adaptor URL registered with the portal", "Only the direct 6443 URL with no Web Adaptor", "Only file shares", "Only the database listener port"),
    q("deploy-enterprise", "Which statement best describes a multi-tier ArcGIS Enterprise architecture?", "Portal, server, and data store can run on separate machines for scaling and isolation", "All components must always run on one machine", "Only ArcGIS Server may be installed", "The relational store must run on the portal machine"),
    q("deploy-enterprise", "Which server role is commonly added when you need dedicated raster analysis tools at scale?", "ArcGIS Image Server as a federated server", "Notebook Server only", "GeoEvent Server only", "Workflow Manager Server only"),
    q("deploy-enterprise", "What does registering a Web Adaptor with ArcGIS Server accomplish?", "Provides a web server–friendly URL and can enforce web-tier authentication policies", "Replaces the need for ArcGIS Data Store", "Installs the portal automatically", "Creates hosted feature layers"),
    q("deploy-enterprise", "Which account model is typical for the ArcGIS Server service account on Windows?", "A domain or local service account with rights to data and config locations", "The built-in Guest account", "A standard user with no file permissions", "The portal administrator only"),
    q("deploy-enterprise", "Which component stores the configuration store for an ArcGIS Server site?", "The ArcGIS Server configuration store (directory or database)", "Portal content directory only", "The Web Adaptor installation folder only", "Client web browsers"),
    q("deploy-enterprise", "For SAML-based enterprise logins to the portal, where is the identity provider relationship configured?", "Portal security settings (SAML identity provider)", "Only in ArcGIS Pro project options", "In the shapefile metadata", "In the tile cache data store only"),
    q("deploy-enterprise", "Which choice best describes the object store in ArcGIS Enterprise 11.x?", "Stores attachments and large binary objects used by certain hosted services", "Replaces the relational data store for all features", "Hosts only ArcGIS Server logs", "Stores only PDF exports"),
    q("deploy-enterprise", "When planning SSL for internal-only access, what is still required for encrypted HTTPS?", "A server certificate trusted by client machines in that environment", "No certificate if the network is private", "Only a database connection file", "A second portal machine"),
    q("deploy-enterprise", "Which guideline applies to the portal content directory?", "Place it on fast, backed-up storage with sufficient space for items and backups", "Store it only on removable USB media", "Share it publicly read/write", "Delete it monthly"),
    q("deploy-enterprise", "ArcGIS Server machines in the same site share which resource?", "A common configuration store and server directories", "Separate unrelated configuration stores per machine", "Only the portal database", "Only local temp folders"),
    q("deploy-enterprise", "Which step is part of authorizing ArcGIS Enterprise software?", "Apply the authorization file and ensure license manager connectivity if used", "Delete all server logs", "Disable the Web Adaptor", "Remove federated servers"),
    q("deploy-enterprise", "What is the purpose of the ArcGIS Data Store 'primary' machine?", "It runs relational, tile cache, or other registered data store roles for the deployment", "It replaces Portal for ArcGIS", "It is only a backup domain controller", "It hosts only ArcGIS Monitor"),
    q("deploy-enterprise", "Which URL pattern do end users typically bookmark for the organization’s apps and portal home?", "The Web Adaptor–exposed HTTPS URL", "arcgisadmin on port 6080 only", "The database ODBC connection string", "file:// paths to map documents"),
    q("deploy-enterprise", "When installing Portal for ArcGIS, what must be decided early and is difficult to change later?", "The portal’s initial administrator account and content directory location", "The color theme of ArcGIS Pro", "The number of map frames in layouts", "Field aliases in a shapefile"),
    q("deploy-enterprise", "Which firewall consideration is most relevant for a federated ArcGIS Server behind a Web Adaptor?", "Allow required ports between Web Adaptor, server, portal, and data store as documented", "Block all traffic on 443", "Open only outbound email", "Disable internal DNS"),
    q("deploy-enterprise", "What does federating ArcGIS Server with Portal enable for publishing workflows?", "Portal-managed hosting, sharing, and security for services", "Removal of all authentication", "Direct-only publishing to shapefiles", "Automatic Kubernetes deployment"),
    q("deploy-enterprise", "Which ArcGIS Server capability is commonly enabled when publishing a map service that will be edited through feature access?", "Feature access (with create/update/delete as required)", "Only KML capability", "WMTS only", "Printing only"),
    q("deploy-enterprise", "For GeoAnalytics Server, what is the typical deployment pattern?", "Install as a separate ArcGIS Server role and federate with the portal", "It replaces the relational data store", "It runs inside a file geodatabase", "It requires no portal"),
    q("deploy-enterprise", "Which item describes the ArcGIS Notebook Server role?", "Hosts ArcGIS Notebooks in the portal ecosystem when licensed and configured", "Stores hosted feature geometry only", "Replaces ArcGIS Web Adaptor", "Manages Active Directory forests"),
    # Troubleshoot (~18%)
    q("troubleshoot-enterprise", "Which log level captures the most verbose diagnostic detail for short-term troubleshooting?", "Debug", "Severe only", "Warning only", "Off"),
    q("troubleshoot-enterprise", "Where should an administrator first look when a map service fails to start after a data path change?", "Server logs and the registered data store path validation", "Only the portal search index", "Browser favorites", "The ArcGIS Pro project’s map frame name only"),
    q("troubleshoot-enterprise", "Users report slow map draws on a busy map service. What is a reasonable first check?", "Service instance settings, cache usage, and underlying data performance", "Delete the portal", "Remove SSL certificates", "Disable the relational data store"),
    q("troubleshoot-enterprise", "If the portal shows a generic error after an upgrade, what should you review first?", "Portal and server logs around the upgrade window", "Only client GPU drivers", "Shapefile spatial indexes only", "Portal organization featured content item count"),
    q("troubleshoot-enterprise", "Intermittent token errors from apps often relate to:", "Clock skew, reverse proxy headers, or Web Adaptor/HTTPS misconfiguration", "Too many layout elements", "Raster pyramids only", "Geodatabase topology rules"),
    q("troubleshoot-enterprise", "A hosted scene layer fails to build. Which component is most relevant to verify?", "Tile cache data store health and space", "Only the print service", "KML network links", "CSV delimiters"),
    q("troubleshoot-enterprise", "What does HTTP 504 from a Web Adaptor often suggest?", "Timeout at the web tier or upstream server overload", "Successful cache hit", "Valid license file", "Empty geodatabase"),
    q("troubleshoot-enterprise", "To trace a specific map request, which approach is appropriate?", "Enable temporary verbose or request-level logging, reproduce, then reduce logging", "Delete all logs permanently", "Disable authentication forever", "Reinstall the OS"),
    q("troubleshoot-enterprise", "If federated server shows 'not reachable' in portal, what should you verify?", "Network reachability, certificates, and Web Adaptor registration URLs", "Only the map scale denominator in the web map JSON", "Field domains in a file GDB", "Layout page size in the print template"),
    q("troubleshoot-enterprise", "Performance degrades after bulk publishing. What should you check?", "Server resources, instance max/min, and database load", "Basemap drawing order in the web map only", "Number of layers in the map document only", "CSV row count in Catalog"),
    q("troubleshoot-enterprise", "Which symptom might indicate the relational data store is stopped or unreachable?", "Failures creating or accessing hosted feature layers", "Only legend font changes", "PDF export margins", "Geocode score display"),
    q("troubleshoot-enterprise", "What is a safe practice after intensive troubleshooting logging?", "Return log levels to standard settings to avoid disk fill and overhead", "Leave Debug on indefinitely", "Delete configuration store", "Block all firewall ports"),
    q("troubleshoot-enterprise", "If printing fails from the portal, which service is most relevant?", "PrintingTools or custom print geoprocessing services", "Hosted tile layer only", "Scene viewer lighting", "Spatial reference names"),
    q("troubleshoot-enterprise", "SSL certificate name mismatch errors in the browser usually mean:", "The certificate CN/SAN does not match the URL users type", "The portal is federated", "A feature class is versioned", "The map uses WGS84"),
    # Maintain and support (~22%)
    q("maintain-support-enterprise", "Which Esri tool is designed to export and restore a Web GIS deployment (portal, server, data store metadata)?", "WebGISDR", "Buffer geoprocessing tool", "Topo to Raster", "XY To Line"),
    q("maintain-support-enterprise", "Before major operating system patches on servers hosting ArcGIS Enterprise, what is a recommended step?", "Take a full backup consistent with Esri guidance and verify recovery procedures", "Delete all hosted layers", "Remove federation", "Disable HTTPS"),
    q("maintain-support-enterprise", "Where can administrators monitor overall portal health and logs in a supported workflow?", "Portal Administrator logs and ArcGIS Server Manager diagnostics", "Windows Event Viewer only without reviewing portal or server logs", "Shapefile .cpg files", "Maplex label engine only"),
    q("maintain-support-enterprise", "What should be validated after restoring from backup?", "Portal and server URLs, services, hosted content, and data store registration", "Only the default rotation of the data frame in saved maps", "Legend patch size in exported PDFs only", "Basemap opacity in one Pro project only"),
    q("maintain-support-enterprise", "When upgrading ArcGIS Enterprise, which guideline is most important?", "Follow Esri-ordered upgrade steps for portal, server, and data store versions", "Upgrade clients only and skip server", "Mix major versions indefinitely", "Delete backups before upgrade"),
    q("maintain-support-enterprise", "Why clear the REST cache in ArcGIS Server during some administrative changes?", "To ensure clients receive updated service definitions and capabilities", "To delete all maps", "To remove SSL", "To shrink file geodatabases"),
    q("maintain-support-enterprise", "Scheduled maintenance windows should include:", "Communication, rollback plan, and verification tests", "Only rebooting without notice", "Deleting the content directory", "Removing all groups"),
    q("maintain-support-enterprise", "Disk space planning for the tile cache data store should account for:", "Growth of hosted tile and scene caches", "Only email attachments", "ArcGIS Pro layout sizes", "KML icon URLs"),
    q("maintain-support-enterprise", "After adding RAM to ArcGIS Server machines, what might you revisit?", "Instance pooling and process memory settings per Esri tuning guidance", "Field precision in shapefiles", "Web adaptor thread count only", "Label halos only"),
    q("maintain-support-enterprise", "Which practice supports stable database connections for enterprise geodatabase services?", "Use supported RDBMS versions, connection pooling, and timely patching", "Store passwords in plain text in maps", "Use retired DB versions", "Share sa passwords publicly"),
    q("maintain-support-enterprise", "What is a key reason to keep portal and ArcGIS Server versions aligned with ArcGIS Data Store?", "Compatibility matrices require matching supported combinations", "They never need to match", "Only the Web Adaptor version matters", "Only ArcGIS Monitor version matters"),
    q("maintain-support-enterprise", "For service performance tuning, increasing what can reduce wait under concurrent load (within hardware limits)?", "Maximum instances of high-load services", "The number of layout elements on the MXD", "PDF DPI for all exports", "Topology rules count"),
    q("maintain-support-enterprise", "Which item should be included in operational runbooks?", "Contact paths, backup schedules, upgrade history, and DR steps", "Only personal social media", "Random map bookmarks", "Unused layer files"),
    q("maintain-support-enterprise", "Why monitor antivirus exclusions carefully on ArcGIS Enterprise hosts?", "Scanning config and data directories can lock files and degrade performance", "Antivirus improves portal search", "Exclusions delete logs", "It replaces backups"),
    q("maintain-support-enterprise", "What should you verify after certificate renewal on the Web Adaptor?", "Portal and server trust the chain and clients connect without warnings", "Only the map extent", "Geodatabase domains", "Label stacking"),
    # Manage content and users (~26%)
    q("manage-content-users", "Which workflow registers an enterprise geodatabase so map services can reference it?", "Register the database with ArcGIS Server (data store item)", "Upload the GDB as a tile package only", "Copy connection files to public web root only", "Email .sde files to external users"),
    q("manage-content-users", "Portal groups are commonly used to:", "Control who can see and edit shared items and collaborate", "Replace the need for ArcGIS Server", "Install software updates", "Manage SSL certificates"),
    q("manage-content-users", "Distributed collaboration between two ArcGIS Enterprise portals typically begins with:", "Sending and accepting a collaboration invitation between organizations", "Sharing one administrator password", "Copying license files between orgs", "Using the same Windows logon"),
    q("manage-content-users", "To allow map services to read from a registered folder, the server account needs:", "Read (and often write) permissions on that folder path", "No permissions", "Only portal administrator rights", "Only email access"),
    q("manage-content-users", "Which sharing level restricts an item to members of specific groups?", "Private to groups (group sharing)", "Public to anyone", "Shared with everyone automatically", "Only offline copies"),
    q("manage-content-users", "When publishing a feature service with editing, which capability must be enabled?", "Feature access with appropriate create/update/delete operations", "Only Map capability", "KML capability only", "Schematics capability only"),
    q("manage-content-users", "Enterprise logins via SAML generally map portal users by:", "Name ID or configured attribute mapping to portal usernames", "Random assignment", "Shapefile FID", "Map scale denominator"),
    q("manage-content-users", "Item dependencies in a web map can include:", "Layers, services, and hosted layers referenced by the map", "Only the Windows hostname", "Only printer drivers", "Only CSV row order"),
    q("manage-content-users", "To bulk-invite members, administrators often use:", "CSV upload or automated provisioning integrated with the identity provider", "Manual one-by-one only with no automation", "Deleting all groups first", "Sharing passwords"),
    q("manage-content-users", "Which task aligns with managing user credit consumption in a portal organization?", "Assign custom roles and monitor usage reports where licensing applies", "Disable all HTTPS", "Remove the data store", "Delete server logs daily"),
    q("manage-content-users", "Collaboration sync workspaces control:", "What content types and direction sync between participant groups", "Only desktop font lists", "SQL Server collation only", "PDF margins"),
    q("manage-content-users", "Registered cloud storage (e.g., S3-compatible) allows:", "Publishing and referencing cloud-backed data where supported", "Replacing Portal for ArcGIS", "Removing Web Adaptor", "Skipping backups"),
    q("manage-content-users", "Custom roles in the portal let you:", "Grant a tailored set of privileges compared to default roles", "Remove all security", "Bypass SAML", "Delete the hosting server"),
    q("manage-content-users", "When a service definition references a copied database on another machine, you must:", "Update data store registration and connection properties to valid paths", "Only change symbology", "Rename the layout", "Clear the portal index only"),
    q("manage-content-users", "Which practice improves content discoverability without changing permissions?", "Use clear titles, tags, and categories", "Hide all metadata", "Remove thumbnails", "Delete descriptions"),
    q("manage-content-users", "Deleting a portal user who owns groups may require:", "Transferring ownership or reassigning content first", "Nothing; groups auto-delete harmlessly always", "Reinstalling ArcGIS Pro on all clients", "Removing SSL"),
    q("manage-content-users", "For hosted feature layers, schema changes visible to consumers often require:", "Republishing or using supported admin workflows for layer definition updates", "Only changing the web map’s initial extent", "Editing PDF exports", "Renaming .mxd files"),
    q("manage-content-users", "Which option describes a collaboration host?", "The portal that creates the collaboration and invites participants", "Any random laptop", "Only ArcGIS Online by policy", "The database sa login"),
    q("manage-content-users", "OAuth apps registered with the portal require:", "Appropriate redirect URIs and client type settings", "A shared sa password", "Removal of Web Adaptor", "Public anonymous access only"),
    q("manage-content-users", "To restrict who can create custom roles, you rely on:", "Portal administrative privileges and organization security policies", "File geodatabase domains", "Maplex settings", "CSV primary keys"),
    # Additional deploy
    q("deploy-enterprise", "The default installation creates an ArcGIS Server site with what relationship to Portal before federation?", "Standalone site that can later be federated", "Always pre-federated with no option", "Only a file share", "Only ArcGIS Online"),
    q("deploy-enterprise", "Which statement about the portal WebContext URL is most accurate?", "It should match how users reach the site through load balancers or Web Adaptors", "It must always use port 6080", "It is optional and unused", "It replaces database TNS names"),
    q("deploy-enterprise", "ArcGIS Enterprise on Linux commonly pairs Portal and Server with:", "Supported web servers and Java Web Adaptor deployments per documentation", "Only IIS", "Only Microsoft Access", "Only shapefiles"),
    q("deploy-enterprise", "When choosing server roles for raster analytics, you consider:", "Imagery volume, analysis patterns, and separate federated server sizing", "Only label halos", "Only CSV encoding", "Raster output format for exports only"),
    q("deploy-enterprise", "Reverse proxy headers must be configured correctly to avoid:", "Incorrect redirect URLs and broken OAuth flows", "Better performance", "Valid SSL", "Hosted layer creation"),
    q("deploy-enterprise", "The ArcGIS Data Store service account must have permissions to:", "Its local directories and connectivity to dependent components", "Nothing; it uses anonymous access", "Only read email", "Only USB devices"),
    # Additional troubleshoot
    q("troubleshoot-enterprise", "If only some layers fail in a web map, check:", "Individual service URLs, permissions, and layer item settings", "Only the portal home page organization description text", "Geodatabase topology only", "Web map bookmark order only"),
    q("troubleshoot-enterprise", "Database authentication failures in server logs often point to:", "Bad credentials, expired passwords, or incorrect data store registration", "Legend patch gaps", "WMS styles", "Label stacking"),
    q("troubleshoot-enterprise", "High CPU on the hosting machine may correlate with:", "Heavy geoprocessing, many service instances, or inefficient queries", "Thumbnail sizes only", "KML name length", "Layout guides"),
    # Additional maintain
    q("maintain-support-enterprise", "Patching ArcGIS Enterprise software typically requires:", "Testing in staging and following Esri patch documentation order", "Patching production first without backup", "Skipping portal patches", "Removing federation before any patch"),
    q("maintain-support-enterprise", "Backup validation should include:", "Test restores on non-production or isolated environments periodically", "Only counting backup files", "Deleting backups after write", "Ignoring data store"),
    q("maintain-support-enterprise", "Service directories on ArcGIS Server should be:", "On reliable storage with monitored free space", "On removable drives only", "Deleted weekly", "Shared world-writable"),
    # Additional manage
    q("manage-content-users", "Content status (e.g., delete protection) can help:", "Prevent accidental deletion of critical web layers", "Force public sharing", "Remove SSL", "Disable logging"),
    q("manage-content-users", "Group managers can typically:", "Invite users and curate items shared to the group", "Reinstall ArcGIS Server silently", "Renew CA certificates automatically", "Patch the RDBMS"),
    q("manage-content-users", "Linking portal members to enterprise groups often uses:", "Group mapping from the identity provider where configured", "Manual copying of shapefiles", "Random GUID assignment", "Portal group sort order in the UI"),
]


def _detect_start():
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
    parser = argparse.ArgumentParser(description="Generate EAEP 2025 practice questions.")
    parser.add_argument(
        "--start", type=int, default=None, metavar="N",
        help="First question number. If omitted, auto-detect from questions.json."
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
            "correctKey": correct_key,
        })
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
