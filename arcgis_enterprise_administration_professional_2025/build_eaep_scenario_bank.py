#!/usr/bin/env python3
"""
Build questions.json: 10 CertFun samples + 90 scenario-based EAEP items
+ 400 (eaep_extra_400.py) + 100 case-study (eaep_extra_100_case_study.py) + 200 themed (eaep_extra_200.py) + 100 ops (eaep_extra_100_ops.py)
+ 100 skills-measured (eaep_extra_100_skills.py)
aligned to EIG domain weights (34 / 18 / 22 / 26 %) within each scenario segment.

Distractors: follow eaep_distractor_design.py (wrong options stay in the same technical domain as the stem).

Run from this folder:
  python build_eaep_scenario_bank.py
Then:
  python build_standalone.py
"""
import hashlib
import json
import os
import random

from eaep_extra_100_case_study import get_extra_100_case_study_scenarios
from eaep_extra_100_ops import get_extra_100_ops_scenarios
from eaep_extra_100_skills import get_extra_100_skills_scenarios
from eaep_extra_200 import get_extra_200_scenarios
from eaep_extra_400 import get_extra_400_scenarios
from eaep_text_rephrase import rephrase_option, rephrase_question_dict, rephrase_stem

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(SCRIPT_DIR, "questions.json")
OLD_PATH = os.path.join(SCRIPT_DIR, "old_questions.json")


def shuffle_options(correct_text, wrong_texts, stem):
    """Deterministic shuffle from stem hash for reproducible banks."""
    opts = [correct_text] + list(wrong_texts)
    h = int(hashlib.sha256(stem.encode("utf-8")).hexdigest(), 16)
    rng = random.Random(h)
    order = list(range(4))
    rng.shuffle(order)
    keys = ["a", "b", "c", "d"]
    shuffled = [opts[i] for i in order]
    correct_key = keys[shuffled.index(correct_text)]
    return [{"key": k, "text": t} for k, t in zip(keys, shuffled)], correct_key


def q(domain, stem, correct, w1, w2, w3):
    stem = rephrase_stem(stem)
    correct = rephrase_option(correct)
    w1, w2, w3 = (rephrase_option(x) for x in (w1, w2, w3))
    opts, ck = shuffle_options(correct, (w1, w2, w3), stem)
    return {
        "domainId": domain,
        "text": stem,
        "options": opts,
        "correctKey": ck,
    }


def load_certfun():
    if os.path.isfile(OLD_PATH):
        with open(OLD_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [dict(x) for x in data.get("questions", [])[:10]]
    return []


# 90 scenario questions: counts deploy 30, troubleshoot 16, maintain 21, manage 23 (matches ~34/18/22/26%)
SCENARIO_SPECS = [
    # --- Deploy ArcGIS Enterprise (30) ---
    ("deploy-enterprise", "A city runs Portal and ArcGIS Server on separate VMs. GIS staff federated the server, but ArcGIS Pro still shows only a direct server connection for publishing—not the portal. The hosting server is set. What is the best next check?", "Confirm users sign in to Pro with the portal URL (same Web Adaptor URL the portal uses), not the raw ArcGIS Server URL.", "Reinstall ArcGIS Data Store on the portal machine.", "Disable the Web Adaptor and use port 6443 only.", "Delete federation and use only built-in accounts."),
    ("deploy-enterprise", "Your security team requires TLS 1.2+ and a public CA certificate for the portal URL. Browsers still warn “not secure.” The .pfx is installed on the Web Adaptor host. What is the most likely production issue?", "The certificate chain or binding does not match the hostname and URL clients use (including SAN), or the site is still reached via HTTP.", "The intermediate CA certificates are missing on the Web Adaptor host, so browsers cannot build a chain to the public root even though the leaf cert is installed.", "The HTTPS binding uses a different hostname than the URL users type (CN/SAN mismatch with the public portal FQDN).", "Users or bookmarks still open the portal over http:// while only https:// is correctly certified."),
    ("deploy-enterprise", "You federated a second ArcGIS Server site for raster analytics. Portal lists it, but image services fail when referenced from hosted web layers. What should you verify first?", "The federated server is reachable from the hosting machine and data paths/credentials for registered stores are valid for that site.", "Merge both sites into one configuration directory.", "Install Portal on the raster server.", "Disable HTTPS on the raster site."),
    ("deploy-enterprise", "SAML login works from the office but fails for remote staff with “redirect_uri mismatch.” VPN is not required. Best explanation?", "The OAuth redirect URIs registered for the portal app do not include the URL users actually use (e.g., different hostname or http vs https).", "The OAuth app registration lists only the internal Web Adaptor hostname; remote staff use the public FQDN, which is absent from allowed redirect URIs.", "Portal’s WebContextURL or organization URL still reflects an old hostname, so the authorization response is sent to a URI the app did not register.", "Remote users are hitting http:// while redirect URIs were registered only for https:// (or the reverse), so the exact string does not match."),
    ("deploy-enterprise", "After changing the portal’s public URL, mobile workers’ Collector links open the old hostname. What is the best administrative response?", "Update organization URL/Web Context settings and communication so all apps and integrations use the new canonical HTTPS URL.", "Rebuild only the tile cache.", "Reinstall ArcGIS Server silently.", "Delete all web maps."),
    ("deploy-enterprise", "A base deployment uses one machine for Portal and one for Server plus Data Store. Leadership wants “HA” by cloning VMs weekly. What is wrong with this as an HA strategy?", "Scheduled clones do not replace supported high-availability patterns; failover and shared state need an architecture designed per Esri guidance, not image copies alone.", "Weekly backups are never useful.", "Portal cannot run on two machines.", "Web Adaptor cannot be installed twice."),
    ("deploy-enterprise", "Users need hosted scene layers. Scene caches build but fail at high LODs. Disk is ample on Server. What component is most suspect?", "Tile cache data store capacity, permissions, or health for large multilevel caches.", "The relational data store is undersized for scene caching (wrong store for deep scene pyramids).", "Scene caches are stored in the portal content directory; expand Portal disk only.", "HTTPS is disabled on the internal 6443 endpoint, so high-LOD tiles fail silently."),
    ("deploy-enterprise", "You register an enterprise geodatabase with ArcGIS Server. Services start, but edits fail with DB errors in server logs. What is a common production cause?", "The ArcGIS Server account lacks DB privileges or the connection file points to a replica that does not allow edits.", "The connection is registered against a read-only connection file or database role while the service exposes editing.", "The enterprise geodatabase is registered with the publishing user's desktop path; the service account resolves a different geodatabase replica.", "DB version compatibility between the Server tier and the geodatabase is unsupported, causing edit operations to fail at the DB driver."),
    ("deploy-enterprise", "An org uses IWA at the web tier. Some REST calls from scripts fail with 401 while browsers work. What is a frequent trap?", "Automated clients do not automatically negotiate IWA; use token/OAuth flows or a service account pattern appropriate for unattended access.", "Disable all authentication.", "Switch Portal to built-in only.", "Open port 6080 to the internet."),
    ("deploy-enterprise", "A city wants real-time IoT sensor feeds processed and published as feature layers in the same portal org. The infrastructure team asks whether GeoEvent Server can simply share the existing hosting server role to avoid licensing another site. What is the correct architecture guidance?", "As its own ArcGIS Server role/site federated with the portal per licensing and architecture—not as a substitute for the hosting server for standard map services.", "GeoEvent processing can be added as a capability to the hosting server site without a separate ArcGIS Server installation.", "GeoEvent Server replaces Portal for ArcGIS as the real-time services endpoint when IoT feeds are involved.", "GeoEvent Server must be installed on the relational data store machine to share the database connection."),
    ("deploy-enterprise", "Notebook Server is federated, but notebooks cannot access data in a registered folder. What is the best first check?", "The ArcGIS Notebook Server run-as account has OS-level read access to the registered folder path.", "Increase map cache.", "Set portal language to English.", "Delete the object store."),
    ("deploy-enterprise", "Reverse proxy forwards /portal to the portal machine but static resources 404. What is often misconfigured?", "Path prefixes, Host headers, or WebSocket/long-polling rules required by Portal are not forwarded correctly by the proxy.", "The proxy forwards `/portal` but strips subpaths such as `/portal/sharing` or static bundles required by the SPA.", "Host header rewrite sends the internal machine name while Portal generates asset URLs for the public hostname.", "TLS termination at the proxy uses a certificate mismatch so static GETs return 404 from an upstream error page."),
    ("deploy-enterprise", "Authorization completes, but Pro says licensing is expired while Portal shows valid. What should you reconcile?", "License user types, add-ons, and provisioning file alignment between Portal and ArcGIS Server, and that Pro is signed into the correct portal.", "Delete all named users.", "Remove Web Adaptor.", "Turn off SAML."),
    ("deploy-enterprise", "You must expose only 443 externally. Internal servers use 7443/6443. What is the correct pattern?", "Terminate TLS at the Web Adaptor (or reverse proxy) and use documented internal ports; do not expose 6443/7443 to the internet without a controlled design.", "Publish 6443 on the public firewall for convenience.", "Bind Portal only to port 80.", "Disable internal HTTPS entirely."),
    ("deploy-enterprise", "Object store is configured for attachments, but hosted layers still cannot store large attachments. What is a likely gap?", "Object store registration/health or size limits versus expectations for hosted attachment storage.", "Raster analytics server is missing.", "The object store only activates for attachments when the relational data store exceeds its default allocation.", "Portal groups are empty."),
    ("deploy-enterprise", "Multi-machine ArcGIS Server site: one machine was rebuilt with a new hostname. The site shows inconsistent. Best practice?", "Remove the old machine cleanly from the site and join the replacement following Esri steps so the configuration store and cluster state stay consistent.", "Copy config folders randomly between servers.", "Run two separate sites with the same config store path.", "Ignore hostname changes."),
    ("deploy-enterprise", "Portal organization requires email verification for new members, but invites never arrive. What is the best check?", "SMTP settings under portal organization email configuration and network allowlisting to the mail relay.", "Rebuild tile cache.", "Increase server instances.", "Disable groups."),
    ("deploy-enterprise", "A team wants separate dev/test/prod portals with the same web map IDs. What is the fundamental issue?", "Item IDs and URLs are portal-specific; promotions require scripted export/import or shared collaboration patterns—not identical IDs across environments.", "You can copy content directories between servers safely without changes.", "Web maps never reference layers.", "Federation merges portals automatically."),
    ("deploy-enterprise", "ArcGIS Server only allows publishing when signed in as the primary admin account. What policy likely applies?", "Privileges/roles or server-level restrictions limit who can publish; adjust custom roles or server security settings rather than sharing the primary admin password.", "This is normal for all sites.", "Disable all custom roles.", "Lower log level to Debug permanently."),
    ("deploy-enterprise", "You add a second data store machine for relational—documentation refers to primary/standby. What is a common misconception?", "Adding a machine does not by itself create supported HA; follow Esri’s documented relational data store HA patterns and version compatibility.", "Two primaries are always valid.", "Standby never needs network to primary.", "Relational store can replace file backups."),
    ("deploy-enterprise", "Web Adaptor and Portal are on different subnets; federation validation fails intermittently. What should you validate first?", "Stable DNS resolution, firewall ports, and time sync between all components involved in the trust relationship.", "Asymmetric firewall rules: return traffic from Portal to the ArcGIS Server admin URL is allowed only during certain maintenance windows.", "Intermittent packet loss on one subnet misclassified as application error; blame the GIS application tier first.", "Stale DNS TTL: one subnet resolves an old IP for the Server admin URL while another resolves the current cluster."),
    ("deploy-enterprise", "Image Server is federated for ortho mosaics, but dynamic image services are slow under load. What is a sensible first tuning lever?", "Service instance min/max, caching strategy, and underlying storage/IOPS for read-heavy rasters—not only adding CPU to Portal.", "Delete pyramids.", "Force JPEG 100% for all exports.", "Disable JPEG compression entirely for imagery."),
    ("deploy-enterprise", "Portal’s default basemap gallery points to the wrong region endpoints. Where is this controlled?", "Portal organization or utility service settings (basemap gallery, geocoding, routing) appropriate to your region and licensing.", "Per-user default basemap in each analyst’s ArcGIS Pro project template overrides the portal for all members.", "The coordinate system of the enterprise geodatabase feature dataset sets which Living Atlas region the portal uses.", "Regional endpoints are selected by the Windows display language on the Portal machine."),
    ("deploy-enterprise", "You enable ‘anonymous access’ for a public dashboard, but layers still prompt. What is the usual reason?", "Layer items or services are not shared to the same level as the app; sharing must be consistent across all dependencies.", "HTTPS is required to be off.", "Web Adaptor must be removed.", "Sharing the app item to Everyone is sufficient; layer items inherit the app's visibility automatically."),
    ("deploy-enterprise", "Corporate policy bans self-signed certs internally. Lab still uses one. Pro trusts it, browsers do not. Best fix for a pilot?", "Deploy an internal CA or enterprise-trusted certificate and distribute trust to clients—not long-term reliance on self-signed exceptions.", "Disable TLS in Portal.", "Map all users to the primary admin.", "Store passwords in connection strings in shared folders."),
    ("deploy-enterprise", "You federate with ‘Server URL’ pointing to a machine name that users cannot resolve externally. What breaks downstream?", "OAuth redirects, service URLs in items, and client configurations must use URLs reachable by every user class; align Web Adaptor public names with DNS.", "VPN users can resolve internal names, so external DNS for the public Web Adaptor hostname does not need to match service URLs in items.", "ArcGIS Online layers in web maps continue to work because they do not use the federated Server URL.", "CSV item uploads fail first because they use a different REST endpoint than hosted layers."),
    ("deploy-enterprise", "A database connection is registered with the server using a desktop path (C:\\users\\…). Services work until that user logs off. Best practice?", "Use stable UNC or server-local paths and a service account with persistent access, not user-profile paths.", "Always use mapped drive letters per user.", "Embed passwords in .mxd only.", "Share the geodatabase over SMB read-only."),
    ("deploy-enterprise", "You need both vector tile and feature services from the same data. What is the deployment consideration?", "Appropriate server roles/capabilities and data store registration support both; ensure hosting and publishing paths match the intended editing vs visualization model.", "Vector tiles replace features automatically.", "Feature layers cannot coexist with tiles.", "A dedicated ArcGIS Server site separate from the hosting server is required to publish vector tiles alongside editable feature services."),
    ("deploy-enterprise", "Portal backup exports are large; leadership wants incremental file copies of the content directory only. What is the risk?", "File-level copies alone may miss consistent application state; use Esri-supported backup/restore tools and documented procedures for recoverability.", "Content directory excludes all items.", "Backups never include databases.", "Incremental copies are always sufficient for Portal."),
    ("deploy-enterprise", "ArcGIS Monitor shows green but users see slow maps. What is the ‘best answer’ interpretation?", "End-user experience depends on service design, data, network, and client; correlate Monitor metrics with service logs and realistic tests—not CPU alone.", "Monitor agent health proves the user experience is acceptable; focus on upgrading desktop GPU drivers.", "Reboot Portal on a schedule whenever Monitor shows green for 24 hours to prevent future slowness.", "Clear the REST service directory cache continuously so every request hits the database cold."),
    # --- Troubleshoot ArcGIS Enterprise (16) ---
    ("troubleshoot-enterprise", "After a Windows patch, hosted layers return ‘Error performing query operation’ while maps draw. Logs show DB connection timeouts. First focus?", "Relational data store / database availability, firewall to DB, and connection pool exhaustion versus generic portal UI errors.", "Reinstall Portal for ArcGIS to reset hosted layer definitions without checking database connectivity.", "Delete and republish all hosted layers to new services without reviewing relational data store or DB logs.", "Point hosted layers at file geodatabase sources instead of the relational data store to avoid DB timeouts."),
    ("troubleshoot-enterprise", "Intermittent 504 from Web Adaptor during morning peak. Server CPU is moderate. What is a plausible bottleneck?", "Web server or reverse-proxy timeout, thread starvation, or upstream ArcGIS Server queueing—not only CPU on one box.", "The Web Adaptor host shows moderate CPU, so the timeout must be a client VPN or Wi-Fi problem—not the gateway or upstream queue.", "Lower reverse-proxy and Web Adaptor upstream timeouts so failed requests fail faster and clear the backlog.", "Raise global min/max service instances on every map service to maximum to eliminate queueing without measuring per-service load."),
    ("troubleshoot-enterprise", "Verbose logging was left on for weeks; disks fill and services crash. Best remediation sequence?", "Reduce log levels to supported baselines, archive or rotate logs per policy, then restore service stability—then investigate original issue with targeted logging.", "Delete the largest log files manually while services are running to free space without a coordinated rotation plan.", "Set all ArcGIS Server and Portal log levels to None permanently to guarantee disk space.", "Expand disk by moving the entire config store to a new volume without stopping services or following Esri procedures."),
    ("troubleshoot-enterprise", "One map service is slow; others on the same machine are fine. Most targeted check?", "That service’s data source, query complexity, instance settings, and whether it hits a different DB or network path.", "Reboot the entire site.", "Rebuild portal index for all org.", "Reinstall ArcGIS Server."),
    ("troubleshoot-enterprise", "Portal log shows ‘Invalid token’ for a single custom app after 12 hours. Others work. Likely cause?", "Token expiration/refresh handling in the app or use of long-lived OAuth refresh tokens versus short-lived access tokens.", "The app caches only the SAML assertion and never exchanges it for new portal tokens after the first session.", "Portal’s OAuth refresh token for that app was revoked; the app still sends an old access token without refreshing.", "The custom app uses a fixed portal token generated once at install; it does not implement refresh before the 12-hour window."),
    ("troubleshoot-enterprise", "Prints fail with a generic error; the same map exports in Pro. What should you inspect first?", "Print service GP logs, output folder permissions, and dependencies (fonts, layers) in the server context—not only the browser.", "The print service output directory points to a user-profile temp path that the ArcGIS Server account cannot write to.", "The web adaptor or reverse-proxy timeout is shorter than the GP print runtime, so the client receives a generic error while the job still runs.", "Custom fonts used in the layout are installed for your desktop user but not for the ArcGIS Server run-as account."),
    ("troubleshoot-enterprise", "CPU spikes on the hosting machine when a single geoprocessing service runs. Users blame ‘Portal’. Best isolation?", "Identify the tool and data volumes; scale GP service instances or optimize the workflow—Portal may be unrelated.", "Always add more portal machines.", "Disable all hosted layers.", "Set all logs to Severe only."),
    ("troubleshoot-enterprise", "SSL inspection at the firewall breaks OAuth. Symptom: random auth failures. Best direction?", "Exclude or properly configure inspection for portal/OAuth endpoints or use pinned TLS per security policy.", "Disable OAuth entirely.", "Open all ports 1–65535.", "Use HTTP only internally."),
    ("troubleshoot-enterprise", "Scene viewer loads but elevation fails. 2D works. Where to look?", "Elevation/terrain layer URLs, HTTPS mixed content, and service availability—not only the scene layer cache.", "The elevation service is blocked by CORS or referrer policy while the scene layer is on the same origin.", "Mixed HTTP/HTTPS: terrain is requested over http:// from an https:// scene page and the browser blocks it.", "The terrain layer endpoint certificate is untrusted or uses a hostname that does not match the SAN, even though the scene layer’s cert is valid."),
    ("troubleshoot-enterprise", "Federated server shows ‘Not reachable’ in portal after cert renewal on Web Adaptor. What is often missed?", "Trust chain on the portal machine for the new cert, and that the admin URL used for federation still validates end-to-end.", "Import the new certificate only into each user’s browser trust store; Portal does not need the chain for server-to-server calls.", "Reproject all map services to Web Mercator so the renewed certificate matches the coordinate system.", "Rename portal collaboration groups to match the new certificate’s subject alternative names."),
    ("troubleshoot-enterprise", "Request-level logging correlates user X with failures, but user insists they did nothing. What else to check?", "Shared accounts, scripts, or AGOL/portal items scheduled to run as that identity.", "Delete user immediately.", "Disable all collaboration.", "Ignore correlation."),
    ("troubleshoot-enterprise", "Antivirus locked files under server directories during peak. Symptom: random service start failures. Best practice?", "Configure AV exclusions for ArcGIS config and server directories per Esri guidance; schedule scans off-peak.", "Disable AV on all servers entirely without policy.", "Move config store to USB.", "Run real-time scan on every REST request."),
    ("troubleshoot-enterprise", "Performance ‘fixed’ by raising service instances to max on all services. Now memory pressure crashes nodes. Lesson?", "Tune instances per service load and hardware; blanket max is a common trap.", "Set max instances to the platform maximum on every service so peak load never queues.", "Set min instances to zero everywhere to minimize memory use regardless of user concurrency.", "Portal memory settings override ArcGIS Server process limits, so raise Portal memory first."),
    ("troubleshoot-enterprise", "Logs show ‘Read timed out’ from portal to hosting server only during backup windows. Likely interaction?", "Backup processes locking I/O or saturating storage/network; coordinate maintenance windows and backup modes with Esri-aware procedures.", "Shorten the backup window by stopping the relational data store service during the snapshot.", "Delete incremental backups to reduce I/O without reviewing backup policy or retention.", "Increase portal-to-server REST timeout values only on the client browsers used by administrators."),
    ("troubleshoot-enterprise", "Custom widget calls REST with HTTP while the site is HTTPS-only. Mixed content blocked. Fix?", "Serve the app over HTTPS and call HTTPS endpoints, or proxy per CSP policy—not disable browser security.", "Downgrade portal to HTTP.", "Embed HTTP iframes only.", "Disable CORS globally."),
    ("troubleshoot-enterprise", "Only one region’s users report slowness. Others fine. First hypothesis?", "Network path, regional egress, or DNS to your entry URL—not an immediate full stack reinstall.", "That region’s subnet still resolves a stale DNS record for the portal or Web Adaptor hostname after a URL change.", "A regional firewall or proxy applies SSL inspection or bandwidth limits only to that office’s egress path.", "All users in that region share one remote desktop host; assume Citrix or VDI GPU saturation before checking the network."),
    # --- Maintain and Support ArcGIS Enterprise (21) ---
    ("maintain-support-enterprise", "You must patch SQL Server hosting the relational data store. What is the correct order mindset?", "Follow Esri and DB vendor ordering: typically validate compatibility, backup, apply DB/OS patches in a tested sequence, then validate ArcGIS—never ad hoc on production first.", "Patch production SQL first without backup.", "Always patch Portal before the database always.", "Skip compatibility matrices."),
    ("maintain-support-enterprise", "Leadership wants zero RPO for Portal. What is realistic?", "Achievable RPO/RTO depends on architecture, backups, and DR tooling (e.g., WebGISDR, DB backups); ‘zero’ requires investment and design—not a checkbox.", "WebGISDR guarantees zero RPO always.", "File copy of content dir is enough.", "Snapshots alone replace databases."),
    ("maintain-support-enterprise", "Upgrade window is 4 hours. Team skipped the full backup ‘to save time.’ Best answer?", "Skipping validated backups before upgrade violates operational best practice; shorten scope or reschedule—do not skip recovery points.", "Upgrades never fail.", "Backups slow upgrades too much always.", "A VM snapshot taken while services are running is equivalent to a validated WebGISDR backup for post-upgrade recovery."),
    ("maintain-support-enterprise", "After upgrade, hosted layers work but search is stale. What maintenance fits?", "Rebuild or refresh the portal search index and verify index location/health per documentation.", "Reinstall ArcGIS Server.", "Delete all items.", "The portal search index refreshes automatically after upgrade; no manual rebuild is needed."),
    ("maintain-support-enterprise", "You restored Portal from backup to a new machine with a different hostname. Logins fail. What principle applies?", "Restores must preserve URL/DNS plans or follow documented rename/rehost procedures; hostnames are embedded in trust flows.", "Hostname never matters.", "Re-importing the license file on the new machine is sufficient to restore federation trust after a hostname change.", "Updating the Windows display name and restarting portal services re-establishes the hostname in all trust flows."),
    ("maintain-support-enterprise", "Service performance tuning: team doubled layer max record counts everywhere. Trade-off?", "Higher limits increase memory and payload size; tune per layer need, not globally, to avoid instability.", "Max record count should always be unlimited so clients never miss features.", "Record count limits only affect print layout and legend spacing, not server memory.", "Doubling max record count only impacts CSV layers, not database-backed layers."),
    ("maintain-support-enterprise", "Monthly vulnerability scan flags TLS ciphers on Web Adaptor. You disable several. Now old clients break. Lesson?", "Balance security baselines with client compatibility; test cipher changes against all required clients.", "Disable TLS entirely.", "Always enable only the newest cipher for everyone.", "Clients never cache TLS."),
    ("maintain-support-enterprise", "Disk on tile cache volume hits 90%. Action priority?", "Plan expansion or cache cleanup strategy before write failures break publishing—not after outage.", "Wait until 100%.", "Move cache to USB.", "Delete relational store to free space."),
    ("maintain-support-enterprise", "DR drill: restore to isolated VLAN. Services start but layers are empty. Common miss?", "Data paths, DNS, and DB connectivity in the DR network differ; validate registrations and firewall rules in the DR context.", "If services start in DR, the databases and data stores must already be consistent—no need to validate connection strings.", "DR must use the same IP addresses as production or ArcGIS Server cannot bind to ports.", "Updating the portal public URL in DNS is sufficient; hosted layer data stores reconnect automatically without testing."),
    ("maintain-support-enterprise", "Organization policy requires yearly key rotation for SAML IdP. After rotation, logins fail. Best first step?", "Update IdP metadata/certificates in portal SAML configuration and validate clock skew—not only restart Portal.", "Delete SAML and use anonymous.", "Rotate only Windows password.", "Updating ArcGIS Pro to the latest version resolves SAML signature validation failures after metadata rotation."),
    ("maintain-support-enterprise", "You schedule WebGISDR during business hours to ‘test’ it. Users report outages. Mistake?", "Run disruptive DR exports during maintenance windows; coordinate impact and use staging environments for practice.", "WebGISDR never touches availability.", "Always run during peak.", "DR tools only backup PDFs."),
    ("maintain-support-enterprise", "Portal health check shows warnings on disk space for indexes. Long-term fix?", "Move or expand index storage per Esri guidance and monitor growth—not repeated temporary deletes.", "Delete search index daily.", "Disable search.", "Put indexes on removable drives."),
    ("maintain-support-enterprise", "After OS patch, ArcGIS Server service will not stay started. Logs point to permissions on directories. What changed operationally?", "Verify the ArcGIS Server account still has ACLs on config and server directories after GPO or security tooling changes.", "Reinstall Windows.", "Always delete config store.", "Change service account daily."),
    ("maintain-support-enterprise", "You optimize by setting every map service to non-pooled. Effect?", "Non-pooled has different resource semantics; misapplied site-wide settings can exhaust processes—tune intentionally.", "Non-pooled map services always reduce latency for every client because each gets a dedicated SOC process.", "Pooled services are deprecated; non-pooled should be the default for all map services.", "Non-pooled only changes how labels are drawn; it does not affect SOC process count or memory."),
    ("maintain-support-enterprise", "Backup retention is 7 days; ransomware hits day 8. Leadership asks why restore failed. Point?", "Retention and immutability policies must match risk tolerance; 7-day windows are a business decision, not a technical surprise.", "Backups are always infinite.", "Ransomware never touches backups.", "Tape is always online."),
    ("maintain-support-enterprise", "Minor version ArcGIS patch available. Team applies only to Portal, not Server. Risk?", "Component version skew can break supported combinations; follow the documented patch order and compatibility matrix.", "Patching one component is always safe.", "Server never needs patches.", "Portal patches include Server always."),
    ("maintain-support-enterprise", "Monitoring alerts on memory on the Data Store machine. Sustained growth. Prudent step?", "Investigate cache growth, logs, and OS metrics; plan capacity before OOM kills—not only silence the alert.", "Restart daily forever.", "Disable monitoring.", "Add RAM without checking workload."),
    ("maintain-support-enterprise", "You clear REST cache after every small change. Users see flapping performance. Better approach?", "Clear cache when definitions change materially; excessive clearing removes beneficial caches and adds load.", "Never clear cache.", "Clear cache every minute.", "Schedule REST cache clears only during designated maintenance windows regardless of whether service definitions changed."),
    ("maintain-support-enterprise", "Staging matches prod versions but uses weaker hardware. Load test shows timeouts. Valid conclusion?", "Staging must be representative for the questions you ask of it; weak hardware yields misleading capacity signals.", "Staging must equal prod exactly always or it is useless.", "Hardware never affects ArcGIS.", "Staging hardware only affects network throughput tests; timeout failures indicate load balancer misconfiguration, not server capacity."),
    ("maintain-support-enterprise", "You document RTO as 4 hours but backups take 6 hours to complete. Issue?", "RTO/RPO must be achievable with your backup/restore architecture; reconcile design or expectations.", "RTO is only a label.", "Faster backup always means less data.", "Restore is always faster than backup."),
    ("maintain-support-enterprise", "GeoEvent or heavy GP pinned to one node; node fails. Design lesson?", "Single points of failure need mitigation at the architecture level; monitoring alone does not replace redundancy plans where required.", "One node is always enough.", "Federation fixes node failure.", "Portal replicates GP automatically."),
    # --- Manage Content and Users in ArcGIS Enterprise (23) ---
    ("manage-content-users", "Two departments share a portal group for collaboration, but each wants different default basemaps for new web maps. Where is the tension?", "Basemap defaults are organization or user experience settings; group collaboration does not override org-level utility/gallery configuration per user subgroup without separate groups/orgs or custom apps.", "Each group can set a different default basemap for its members without org admin changes.", "Each department should use a separate Portal for ArcGIS deployment to get different basemap galleries.", "Basemap defaults are stored in the group owner’s content folder and apply to all shared items."),
    ("manage-content-users", "Distributed collaboration: edits in Org A do not appear in Org B’s group after a day. What is a common configuration trap?", "Sync schedule, workspace direction, and content types allowed for sync—not only ‘collaboration exists’.", "Collaboration is always real-time.", "B groups cannot receive edits.", "Sync direction is determined solely by which org sent the collaboration invitation, not by workspace configuration."),
    ("manage-content-users", "You register an AWS S3 bucket as a cloud store. Publishing fails with access denied. Best first check?", "IAM policy, endpoint, and ArcGIS Server/cloud store credentials match the bucket policy and region—not only portal admin rights.", "S3 does not work with ArcGIS.", "Access denied on S3 always indicates an IAM policy issue on the portal machine rather than the ArcGIS Server service account.", "Disable HTTPS for S3."),
    ("manage-content-users", "Custom role allows publishing but user still cannot share to a group. Why?", "Group membership and group capabilities (who can share/update) constrain sharing beyond role privileges.", "Roles override all group rules always.", "Publishing ignores groups.", "Custom roles that include publishing automatically grant permission to share to any group the user is a member of."),
    ("manage-content-users", "Enterprise logins create duplicate usernames with different domains. Messy ownership. Prevention?", "Consistent attribute mapping and IdP name ID strategy agreed with IdP admins—not ad hoc portal invites.", "Portal cannot use SAML.", "Duplicates are impossible.", "Enterprise logins from different AD domains are always disambiguated by portal using the email attribute automatically."),
    ("manage-content-users", "You want contractors to see maps but not export data. Best lever?", "Layer and service capabilities (query, export) combined with custom roles and item settings—not only hiding the print button in one app.", "Hide the Export menu in Pro only.", "Security through obscurity in PDF DPI.", "Disable HTTPS."),
    ("manage-content-users", "Collaboration host migrates portal URL. Participants still point to old invitations. Fix?", "Update collaboration connections and re-establish trust per migration procedures; invitations embed endpoints.", "Invitations auto-update.", "Collaboration ignores URLs.", "Updating DNS on participant portal machines is sufficient to redirect collaboration endpoints after a URL migration."),
    ("manage-content-users", "‘Everyone’ sharing is disabled org-wide, but a manager demands a public dashboard by tomorrow. Best answer?", "Explain org policy boundaries; use approved public-facing mechanisms or policy exception processes—not bypassing security with shared passwords.", "Use primary admin for public items always.", "Disable org security temporarily.", "Publish to anonymous file share."),
    ("manage-content-users", "Database registration uses OS authentication, but the service runs as a domain account that cannot see the DB. Trap?", "Alignment between the account running the service and the DB authentication model (OS auth vs DB auth) and SPNs where applicable.", "OS auth never works with ArcGIS.", "Always use sa login.", "Registration ignores accounts."),
    ("manage-content-users", "Group owner leaves the company. Content is locked. Prevention?", "Transfer group ownership and content before account deletion; use admin recovery workflows per policy.", "Groups auto-delete with user always safely.", "Portal deletes content automatically.", "Portal automatically reassigns group ownership to the next alphabetical active member when the owner account is deleted."),
    ("manage-content-users", "You enable update capabilities on a feature service backed by versioned enterprise GDB. Editors see conflicts. Operational expectation?", "Versioned workflows require reconciliation/post processes; ‘just turn on editing’ ignores DB concurrency design.", "Versioning removes all conflicts.", "Hosted layers only can be versioned.", "Conflicts mean Portal is broken."),
    ("manage-content-users", "OAuth app redirect URIs list localhost for dev only. Production users fail. Fix?", "Register production URIs and use separate apps or conditional registration—not localhost in prod.", "OAuth allows any redirect automatically.", "Always use one URI for all environments.", "Disable OAuth for prod."),
    ("manage-content-users", "Org wants ‘read-only’ maps but WFS exposes full schema. Risk?", "Service capabilities and OGC exposure must match data sensitivity; read-only UX does not secure the protocol.", "If the web map does not show an edit template, WFS cannot return attributes.", "OGC WFS and WMS are blocked by the portal firewall while REST is allowed.", "Disabling the map’s pop-up in the web map prevents WFS GetFeature from returning fields."),
    ("manage-content-users", "Multiple portals federate the same ArcGIS Server site by mistake. Symptom?", "Unsupported overlapping federation scenarios cause trust and publishing conflicts; one portal should own a given server site pattern per design.", "This is supported for HA.", "Federation merges portals.", "Second portal becomes read-only automatically."),
    ("manage-content-users", "Content dependency report shows a web map points to a deleted layer item. User blames portal outage. Best response?", "Repair or replace broken item references in the web map; dependencies are item-level integrity, not platform uptime.", "Restart Portal only.", "Delete the web map silently.", "Escalate to the network team for packet loss without checking item dependencies or broken layer URLs."),
    ("manage-content-users", "You register the same database twice with different names. Services behave inconsistently. Lesson?", "Avoid duplicate registrations confusing admins; use one registration and clear naming conventions.", "Duplicate registration is a best practice for separating dev and prod services on one site.", "ArcGIS Server merges duplicate datastore entries at runtime so behavior should be identical.", "Duplicate registrations only change symbology for OGC WMS GetMap responses, not REST map services."),
    ("manage-content-users", "Cloud data store + on-prem Server: latency causes timeouts on large extracts. ‘Fix’ requested by buying faster laptops. Best answer?", "Address network architecture, service limits, and extract patterns; client CPU is rarely the root cause for server timeouts.", "Approve faster laptops for analysts so the extract completes before the client-side timeout.", "Move all cloud data to local shapefiles on the Server machine to eliminate network latency.", "Increase Pro map frame DPI so the server returns smaller payloads."),
    ("manage-content-users", "Portal members imported from AD group; someone removed in AD still appears in portal. Explanation?", "Group sync is periodic and subject to portal configuration; verify sync schedules and conflict resolution—not instant removal guarantees in all setups.", "AD changes are instant always.", "Portal ignores AD after import.", "Portal removes enterprise users immediately on the next sign-in attempt after their AD account is disabled."),
    ("manage-content-users", "You need two-way collaboration between agencies with different security labels. Barrier?", "Legal and policy constraints may forbid automated sync; technical collaboration must align with information governance—not only portal settings.", "Portal enforces legal clearance automatically.", "Labels are cosmetic.", "Collaboration bypasses classification."),
    ("manage-content-users", "Hosted feature layer schema change requested in production Friday 4pm. Best practice?", "Use change windows, staging validation, and controlled republish; schema changes have downstream app effects.", "Always change production Friday evening without staging.", "Schema changes never break apps.", "Schema changes to hosted feature layers affect only ArcGIS Pro connections; web apps and REST API clients continue without interruption."),
    ("manage-content-users", "Shared update group: two curators delete the same item. Outcome?", "Last operation wins unless versioned workflows exist elsewhere; governance and locks matter for critical layers.", "Portal prevents all deletes.", "Deletes merge automatically.", "Portal queues concurrent delete operations in shared update groups and applies them in sequence to prevent data loss."),
    ("manage-content-users", "Credit-consuming tools enabled org-wide. Finance sees a spike from one project. Control?", "Assign roles, custom privileges, and monitor usage/credits; not everyone needs premium capabilities.", "Credits are unlimited in Enterprise.", "Portal cannot track usage.", "In ArcGIS Enterprise, premium tool consumption is tracked org-wide and cannot be allocated or capped per project or team."),
    ("manage-content-users", "You publish a map service with ‘everyone’ visibility but data source is restricted at the DB. Symptom?", "Service may start yet data access fails for non-privileged DB users; align DB grants with service account—not only portal sharing.", "Portal sharing fixes DB grants automatically.", "Everyone means OS admin.", "DB permissions do not apply to map services."),
]


def main():
    certfun = [rephrase_question_dict(dict(x)) for x in load_certfun()]
    if len(certfun) != 10:
        raise SystemExit(
            "Expected 10 CertFun questions in old_questions.json; found {}. Restore or place old_questions.json.".format(
                len(certfun)
            )
        )

    extra_400 = get_extra_400_scenarios()
    extra_100 = get_extra_100_case_study_scenarios()
    extra_200 = get_extra_200_scenarios()
    extra_100_ops = get_extra_100_ops_scenarios()
    extra_100_skills = get_extra_100_skills_scenarios()
    all_specs = (
        list(SCENARIO_SPECS)
        + list(extra_400)
        + list(extra_100)
        + list(extra_200)
        + list(extra_100_ops)
        + list(extra_100_skills)
    )
    if len(SCENARIO_SPECS) != 90:
        raise SystemExit("SCENARIO_SPECS must be 90, got {}".format(len(SCENARIO_SPECS)))
    if len(extra_400) != 400:
        raise SystemExit("eaep_extra_400 must be 400, got {}".format(len(extra_400)))
    if len(extra_100) != 100:
        raise SystemExit("eaep_extra_100_case_study must be 100, got {}".format(len(extra_100)))
    if len(extra_200) != 200:
        raise SystemExit("eaep_extra_200 must be 200, got {}".format(len(extra_200)))
    if len(extra_100_ops) != 100:
        raise SystemExit("eaep_extra_100_ops must be 100, got {}".format(len(extra_100_ops)))
    if len(extra_100_skills) != 100:
        raise SystemExit("eaep_extra_100_skills must be 100, got {}".format(len(extra_100_skills)))

    scenarios = []
    for domain, stem, corr, w1, w2, w3 in all_specs:
        scenarios.append(q(domain, stem, corr, w1, w2, w3))

    if len(scenarios) != 990:
        raise SystemExit("Scenario count must be 990, got {}".format(len(scenarios)))

    all_q = []
    for i, raw in enumerate(certfun + scenarios):
        item = {
            "id": "q{}".format(i + 1),
            "domainId": raw["domainId"],
            "text": raw["text"],
            "options": raw["options"],
            "correctKey": raw["correctKey"],
        }
        all_q.append(item)

    out = {
        "examId": "EAEP_2025",
        "source": (
            "Aligned to EAEP2025_EIG_JAN2026.pdf. Questions 1–10: scenario/case-study stems from old_questions.json "
            "(topics aligned to common EAEP sample areas; four options each). Questions 11–100: core scenario bank; questions 101–500: eaep_extra_400.py; "
            "questions 501–600: eaep_extra_100_case_study.py; questions 601–800: eaep_extra_200.py; "
            "questions 801–900: eaep_extra_100_ops.py (usage vs Monitor, ports/DMZ, maintenance, WebGISDR, groups/roles, tokens, LDAP, WebContext, Server account); "
            "questions 901–1000: eaep_extra_100_skills.py (EIG skills-measured themes: deploy, troubleshoot, maintain, manage—Monitor, data stores, federation/additional sites, airgap auth, collaboration, usage reports, publishing access). "
            "Built by build_eaep_scenario_bank.py. "
            "Not affiliated with Esri."
        ),
        "questions": all_q,
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print("Wrote {} questions to {}".format(len(all_q), OUT_PATH))


if __name__ == "__main__":
    main()
