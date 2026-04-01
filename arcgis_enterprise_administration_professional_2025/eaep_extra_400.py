#!/usr/bin/env python3
"""
400 additional EAEP-style scenario tuples (best-answer, plausible distractors).
Domain weights match EIG: deploy 34%, troubleshoot 18%, maintain 22%, manage 26%
=> 136 / 72 / 88 / 104 out of 400.

Topics emphasize SSO/SAML/OAuth, enterprise authentication, Web Adaptor/IWA,
Active Directory/LDAP group sync, 3D/scene layers, tile/scene caches, backup/WebGISDR/DR.

Distractor policy: see eaep_distractor_design.py — wrong options stay in the same problem domain
as the stem (TLS vs chain/binding, OAuth vs redirect URIs, etc.).
"""
def _d(stem, *args):
    """Stem + either (correct, w1, w2, w3) or one tuple of four answer strings."""
    if len(args) == 4 and all(isinstance(a, str) for a in args):
        correct, w1, w2, w3 = args
    elif len(args) == 1 and isinstance(args[0], tuple) and len(args[0]) == 4:
        correct, w1, w2, w3 = args[0]
    else:
        raise ValueError("Expected stem and four answer strings or one 4-tuple.")
    return (stem, correct, w1, w2, w3)


_IDPS = [
    "Okta",
    "Azure AD",
    "ADFS",
    "PingFederate",
    "Google Workspace SAML",
    "Keycloak",
    "OneLogin",
    "Auth0",
]

_NETS = [
    "branch offices in two countries",
    "a split-tunnel VPN",
    "a ZTNA gateway",
    "a legacy HTTP-only intranet zone",
    "a guest Wi-Fi segment",
    "a VDI farm",
    "a reverse proxy at the edge (HTTPS to clients)",
    "a cloud egress proxy",
]

def _deploy_sso_block():
    """40 deploy: SAML/OAuth/enterprise login setup."""
    issues = [
        _d(
            "The IdP returns a SAML assertion, but Portal shows 'The account could not be logged in' before any group page loads.",
            (
                "Verify NameID / attribute mapping matches portal enterprise login configuration and that required claims are released for ArcGIS.",
                "Re-import portal enterprise login metadata without updating the NameID attribute mapping.",
                "Update the portal Web Context URL but leave the SAML redirect URI unchanged.",
                "Flush the portal token cache to force re-authentication for all enterprise users.",
            ),
        ),
        _d(
            "OAuth authorization succeeds, but the redirect lands on an error page with 'redirect_uri' in the message.",
            (
                "Ensure the OAuth app registration includes every redirect URI clients use (environment, hostname, and scheme).",
                "Register only the internal Web Adaptor hostname in the app, assuming external URLs resolve to the same endpoint.",
                "Increase token expiry to 24 hours so the redirect timeout is less likely to fire.",
                "Use the portal organization URL as the redirect URI and assume all apps share the same registered endpoint.",
            ),
        ),
        _d(
            "SAML works for browsers, but ArcGIS Pro federated login fails with certificate errors.",
            (
                "Confirm the machine trusts the IdP and portal TLS chains (enterprise roots, proxy inspection) for the Pro process context.",
                "Trust only the portal web certificate in the user store; Pro does not need the IdP signing chain.",
                "Sign in to Pro using the raw ArcGIS Server URL (6443) instead of the portal URL to bypass SAML.",
                "Update the portal’s HTTPS binding certificate and assume Pro automatically picks up the new chain.",
            ),
        ),
        _d(
            "After IdP certificate rollover, logins fail with signature validation errors.",
            (
                "Import updated IdP metadata or signing certificate into the portal SAML configuration and clear stale metadata.",
                "Rotate only the Windows service account password.",
                "Set ArcGIS Server log level to Debug on all services indefinitely to capture the next failure.",
                "Update the portal’s own TLS certificate and assume SAML signature validation refreshes automatically.",
            ),
        ),
        _d(
            "Enterprise logins are enabled, but new users are not provisioned into the expected default role.",
            (
                "Review SAML attribute mapping and default role / group rules tied to enterprise login—not only the IdP login success.",
                "Verify the portal’s HTTPS Web Adaptor URL matches the IdP callback URL exactly.",
                "Disable the portal search index rebuild so new accounts appear without delay.",
                "Set all services to non-pooled to reduce authentication load during provisioning.",
            ),
        ),
    ]
    rows = []
    for issue in issues:
        stem, a, b, c, d = issue
        for idp in _IDPS:
            rows.append(
                _d(
                    "Portal uses SAML with {idp}. ".format(idp=idp) + stem,
                    a,
                    b,
                    c,
                    d,
                )
            )
    return [("deploy-enterprise",) + x for x in rows]


def _deploy_cache_3d_block():
    """32 deploy: tile cache, scene, 3D, LOD."""
    backs = [
        "direct-attached SSD",
        "SAN LUN",
    "SMB share for cache",
    "fast NAS with snapshots",
    "NVMe on the hosting machine",
    "replicated storage for DR",
    "local RAID with thin provisioning",
    "cloud block storage",
    ]
    issues = [
        _d(
            "Hosted scene layer caching progresses through mid-LODs then stalls; disk throughput looks healthy.",
            (
                "Check tile cache data store health, permissions, and free space for deep multilevel caches; scene caches can fail late in the pyramid.",
                "Increase Server max record count so more cache tiles are written per job.",
                "Re-register the tile cache data store using an alternate service account.",
                "Set every map service to a single instance only.",
            ),
        ),
        _d(
            "You publish a scene layer; the cache job completes but clients see missing tiles at the finest scale.",
            (
                "Validate coordinate system, tiling scheme alignment, and that the service exposes expected LODs without client scale clamping issues.",
                "Re-publish the scene service using a different tiling scheme to force cache regeneration.",
                "Increase the server’s max instances so cache jobs run in parallel.",
                "Disable compression on all vector tile packages so each tile is maximum size for quality.",
            ),
        ),
        _d(
            "A 3D mesh scene layer draws but flickers or disappears at certain camera angles.",
            (
                "Investigate multipatch/mesh service behavior, vertical datum/elevation sources, and client GPU limits—not only portal branding.",
                "Increase server log verbosity to FINE and assume the next cache run self-corrects.",
                "Reduce the service’s max scale level so the flicker-prone LODs are never requested.",
                "Move the tile cache data store to a slower NAS to reduce fragmentation.",
            ),
        ),
        _d(
            "Vector tile layers load, but the accompanying elevation surface fails in Scene Viewer over HTTPS.",
            (
                "Check mixed content, certificate trust, and that elevation/terrain endpoints match the site's HTTPS requirements.",
                "Remove the elevation service from the web scene and use a flat terrain assumption.",
                "Set the elevation service to non-pooled to isolate HTTPS failures per request.",
                "Switch the web scene to use the ArcGIS Online World Elevation service without validating SAN.",
            ),
        ),
    ]
    rows = []
    for issue in issues:
        stem, a, b, c, d = issue
        for back in backs:
            rows.append(
                _d(
                    "ArcGIS Server hosts scene and tile workloads on {back}. ".format(back=back) + stem,
                    a,
                    b,
                    c,
                    d,
                )
            )
    return [("deploy-enterprise",) + x for x in rows]


def _deploy_fed_ssl_block():
    """32 deploy: federation, SSL, WA, HA."""
    hosts = [
        "portal.contoso.com",
        "gis.city.gov",
        "maps.agency.org",
        "enterprise.example.net",
        "wa.internal.corp",
        "geo.publicworks.local",
        "sdept.region.state",
        "arcgis.utility.co",
    ]
    issues = [
        _d(
            "Federation validation passes, but OAuth redirects in items still reference an old hostname.",
            (
                "Update portal system properties / WebContextURL and dependent URLs so OAuth and items use the canonical public name consistently.",
                "Point both machines at the same config store folder without granting modify rights.",
                "Re-federate the server using the internal machine name instead of the public FQDN.",
                "Update only the portal system properties and skip the server admin URL update.",
            ),
        ),
        _d(
            "You terminate TLS at the Web Adaptor; internal tests to 6443 work but external users see certificate warnings.",
            (
                "Align the certificate SAN/CN with the public URL users type, and verify the chain is served at the client-facing endpoint.",
                "Install the PFX on the Portal machine only; browsers talk to Portal directly, not the Web Adaptor.",
                "Use the internal machine name on the certificate while users browse by public DNS alias without SAN entries.",
                "Trust the self-signed cert on the Web Adaptor internally and expect public CA trust to follow automatically.",
            ),
        ),
        _d(
            "A second ArcGIS Server machine joins the site, but the site remains unhealthy for shared config paths.",
            (
                "Follow Esri multi-machine steps for permissions, shared config store, and hostname/DNS so all nodes agree on cluster state.",
                "Add the second machine to the site using a different config store path.",
                "Configure both machines with separate config stores and rely on load balancer for state.",
                "Share the config store folder but omit granting the service account modify rights.",
            ),
        ),
        _d(
            "Reverse proxy rules send /portal traffic, but Portal WebSocket or long-polling features break intermittently.",
            (
                "Adjust proxy timeouts, WebSocket upgrade rules, and Host header forwarding per Esri reverse-proxy documentation.",
                "Increase Web Adaptor timeout to 300 s and leave WebSocket upgrade rules unchanged.",
                "Adjust only the proxy’s SSL cipher list and assume WebSocket handling is unaffected.",
                "Forward Host headers as the internal machine name and rely on portal URL rewriting.",
            ),
        ),
    ]
    rows = []
    for issue in issues:
        stem, a, b, c, d = issue
        for h in hosts:
            rows.append(
                _d(
                    "The public entry hostname is {h}. ".format(h=h) + stem,
                    a,
                    b,
                    c,
                    d,
                )
            )
    return [("deploy-enterprise",) + x for x in rows]


def _deploy_general_block():
    """32 deploy: mixed (Notebook, GeoEvent, DB, IWA scripts)."""
    ctx = _NETS
    issues = [
        _d(
            "Automated Python scripts using the Sharing REST API fail with 401 while interactive browsers succeed with IWA.",
            (
                "Use token-based or OAuth flows appropriate for unattended access; scripts do not perform interactive IWA negotiation like browsers.",
                "Configure the script to send cookies from a cached browser session.",
                "Add the script host to the IWA trusted-hosts list and rely on Negotiate for all clients.",
                "Switch the Web Adaptor to NTLM-only mode so scripts can authenticate without Kerberos tickets.",
            ),
        ),
        _d(
            "Notebook Server cannot read data in a registered folder used by other services.",
            (
                "Grant the Notebook Server run-as account OS-level access to the registered folder path and verify UNC vs local path consistency.",
                "Register the folder using a local path on the Notebook Server machine rather than a UNC path.",
                "Grant access only to the portal service account and assume Notebook Server inherits it.",
                "Re-register the folder using the Portal admin credentials instead of the Notebook run-as account.",
            ),
        ),
        _d(
            "GeoEvent is federated; outputs to feature services fail under load while inputs are healthy.",
            (
                "Validate service scale (instances), data store registration, and DB throughput for the target services—not only GeoEvent CPU.",
                "Reduce GeoEvent input rate to match the feature service’s single-instance write throughput.",
                "Increase GeoEvent output retry interval and assume the feature service catches up.",
                "Bypass the Web Adaptor for GeoEvent outputs and connect directly to Server port 6443.",
            ),
        ),
        _d(
            "An enterprise geodatabase is registered; publishing works but versioned editing conflicts spike after peak hours.",
            (
                "Review versioning workflows, reconcile schedules, and DB behavior; peak editing may need branch/version policy tuning.",
                "Switch all editors to the DEFAULT version to avoid reconcile conflicts.",
                "Increase the DB transaction log size to absorb peak-hour edit volume without reconciling.",
                "Delete all named versions and rely on DEFAULT version for all concurrent editing.",
            ),
        ),
    ]
    rows = []
    for issue in issues:
        stem, a, b, c, d = issue
        for n in ctx:
            rows.append(
                _d(
                    "The deployment serves users behind {n}. ".format(n=n) + stem,
                    a,
                    b,
                    c,
                    d,
                )
            )
    return [("deploy-enterprise",) + x for x in rows]


def _troubleshoot_block():
    """72 troubleshoot: SSO, cache, 3D, auth, DR symptoms."""
    tags = list(range(8))
    issues = [
        _d(
            "SAML logins fail after a daylight-saving change only for users in one region.",
            (
                "Check clock skew between IdP, portal, and clients; SAML validity windows are time-sensitive.",
                "Update portal time-zone settings and assume the IdP adjusts its validity window automatically.",
                "Reconfigure SAML to use a longer assertion validity period without adjusting clocks.",
                "Re-export the IdP metadata after DST and re-import into portal without restarting.",
            ),
        ),
        _d(
            "OAuth works until a corporate SSL inspection appliance was enabled; mobile apps now fail randomly.",
            (
                "Configure inspection bypass or pinned TLS for portal/OAuth endpoints per security policy, or distribute proper trust.",
                "Bypass SSL inspection only for the hosting server but not for the IdP endpoint.",
                "Distribute the inspection appliance’s root cert to Portal but not to mobile app trust stores.",
                "Update only the Portal TLS cert and ignore the Web Adaptor binding.",
            ),
        ),
        _d(
            "Scene Viewer shows a flat globe; terrain and elevation do not draw though the 2D map is fine.",
            (
                "Verify terrain/elevation layer URLs, HTTPS/mixed content, and that services respond at the scales Scene Viewer requests.",
                "Re-register the elevation layer as a map service instead of an image service.",
                "Clear the Scene Viewer cache in Portal and republish the web scene without the elevation surface.",
                "Switch the scene to local mode to bypass terrain rendering without diagnosing the root cause.",
            ),
        ),
        _d(
            "Tile layers show stale content after an update; clearing REST cache did not help consistently.",
            (
                "Investigate CDN/proxy caches, service cache update mode, and whether clients or reverse proxies retain old tiles.",
                "Set the tile service update mode to RECREATE and assume downstream proxies expire old tiles.",
                "Purge only the ArcGIS Server REST cache and assume CDN and browser caches self-expire.",
                "Clear tiles from the tile cache data store manually and skip the CDN invalidation step.",
            ),
        ),
        _d(
            "Federated server shows intermittent 'Not reachable' after firewall rule changes.",
            (
                "Validate required ports and stable DNS between portal and server admin URLs, including return paths and time sync.",
                "Update only the portal admin URL and leave the server admin URL pointing to the old hostname.",
                "Restart ArcGIS Server on all nodes without verifying the firewall rule change scope.",
                "Re-federate using the server machine name instead of its DNS FQDN.",
            ),
        ),
        _d(
            "Custom web app tokens expire every hour; long-running edits fail though the map still pans.",
            (
                "Implement refresh tokens or app-specific token renewal; short-lived OAuth tokens require proper refresh handling.",
                "Extend the portal token lifetime to 24 hours org-wide to avoid refresh complexity.",
                "Use the primary site administrator token for all long-running client sessions.",
                "Switch to built-in authentication to avoid OAuth token expiry issues entirely.",
            ),
        ),
        _d(
            "GP service succeeds in Pro but fails in the portal print widget with the same map.",
            (
                "Inspect print service logs, output folder permissions, and server-side fonts/paths; server context differs from desktop.",
                "The portal print widget calls a different GP print service URL than ArcGIS Pro; align only the client without checking Server logs.",
                "Clear the portal’s tile cache and republish basemaps to fix the print widget rendering.",
                "Increase Web Adaptor timeout from 60 s to 300 s without checking print service logs.",
            ),
        ),
        _d(
            "Only users from one AD site fail IWA through the Web Adaptor; others succeed.",
            (
                "Check DNS SRV/hostname resolution, Kerberos delegation constraints, and trust paths for that site—not only portal roles.",
                "Switch the Web Adaptor to NTLM-only mode to remove Kerberos delegation from the equation.",
                "Add the affected users to a built-in portal group as a workaround without fixing Kerberos.",
                "Set all services to non-pooled to reduce authentication load during provisioning.",
            ),
        ),
        _d(
            "After a storage migration, hosted scene layers error when building caches at fine levels.",
            (
                "Verify new paths, permissions, and free space for tile cache data store and that latency/IOPS meet cache build needs.",
                "Re-register the tile cache data store pointing to the old storage path.",
                "Re-publish the scene layer from scratch without verifying write permissions on the new path.",
                "Increase tile cache data store allocation without confirming the new storage IOPS.",
            ),
        ),
    ]
    rows = []
    for issue in issues:
        stem, a, b, c, d = issue
        for t in tags:
            rows.append(
                _d(
                    "[Diag case {t}] ".format(t=t + 1) + stem,
                    a,
                    b,
                    c,
                    d,
                )
            )
    return [("troubleshoot-enterprise",) + x for x in rows]


def _maintain_block():
    """88 maintain: backup, WebGISDR, cache, patches, SAML rotation."""
    tags = list(range(8))
    issues = [
        _d(
            "Leadership demands proof of restore; full WebGISDR export has never completed in the maintenance window.",
            (
                "Validate storage throughput, staging space, and schedule length; tune DR procedures and hardware to meet achievable RTO.",
                "Run WebGISDR without the staging area on a local SSD and assume network transfer is the bottleneck.",
                "Skip compressing the export archive and assume the maintenance window can be extended ad hoc.",
                "Schedule the export concurrently with business hours to verify it completes under real load.",
            ),
        ),
        _d(
            "After restoring Portal to a DR site, hosted layers exist but data is empty.",
            (
                "Ensure relational/tile stores and backups are restored consistently and connection strings/DNS match the DR network design.",
                "Restore only the content directory and update DNS to point to the DR portal.",
                "Restore Portal and Server but defer data store recovery until hosted layers error out.",
                "Re-register data stores after restore without verifying connection string DNS alignment.",
            ),
        ),
        _d(
            "Automated SQL backups run, but transaction log growth threatens disk during heavy editing.",
            (
                "Tune recovery model, log backups, and monitoring for the relational data store workload—not only full backups.",
            "Switch the geodatabase to simple recovery model without assessing edit volume.",
            "Schedule full DB backups every hour as a substitute for transaction log backups.",
            "Increase the data store’s allocated disk and assume log growth is self-limiting.",
            ),
        ),
        _d(
            "Yearly SAML IdP metadata rotation is due; you postpone testing until production day.",
            (
                "Stage metadata/cert updates in a test portal or maintenance window with rollback; SAML changes are high impact.",
                "Apply the new metadata immediately in production and roll back if logins fail.",
                "Update the metadata only on Portal and defer the matching Server configuration update.",
                "Re-import the old metadata certificate and assume the new one validates against it.",
            ),
        ),
        _d(
            "Tile cache volume exceeds 85% and new publishing fails sporadically.",
            (
                "Plan expansion or cache lifecycle cleanup before outage; monitor growth and align with retention policies.",
                "Delete the oldest tile scales first and assume new publishing will fit in reclaimed space.",
                "Move only the most recently published cache to external storage without updating the data store path.",
                "Increase the tile data store allocation without verifying available disk on the hosting machine.",
            ),
        ),
        _d(
            "You clear REST cache aggressively after every map service edit; users report unpredictable performance.",
            (
                "Clear cache when service definitions materially change; excessive clearing removes beneficial caching and adds load.",
                "Automate cache clears on a 15-minute schedule to ensure clients always see the latest definition.",
                "Disable service-level REST cache entirely and rely only on browser caching.",
                "Clear cache only at portal level and assume server-level REST cache is a separate layer.",
            ),
        ),
        _d(
            "Patch Tuesday applied; ArcGIS Server account lost modify rights on server directories.",
            (
                "Restore ACLs for the ArcGIS Server account on config and directories after GPO or security tool changes.",
                "Re-run ArcGIS Server authorization after Patch Tuesday to restore directory rights.",
                "Re-install ArcGIS Server over the existing installation to refresh ACLs.",
                "Grant full control to all service accounts to pre-empt future Patch Tuesday ACL resets.",
            ),
        ),
        _d(
            "DR policy requires immutable backups; ransomware exercise shows tape copies were overwritten.",
            (
                "Implement immutability/WORM or offline copies per risk tolerance; backup policy must match recovery goals.",
                "Use daily snapshots on the same storage array and classify them as immutable by policy.",
                "Enable S3 versioning without object-lock and assume versioning counts as immutability.",
                "Store backups on a writable share accessible from the production servers for fast restore.",
            ),
        ),
        _d(
            "Minor ArcGIS patch is applied to Portal only; federated publishing breaks.",
            (
                "Follow supported component version matrices and documented patch order; skewed versions can break supported combinations.",
                "Patch Portal first and assume Server compatibility is maintained across minor versions.",
                "Apply all patches simultaneously across Portal, Server, and Data Store in one maintenance window.",
                "Skip Data Store patching if Portal and Server report healthy post-patch.",
            ),
        ),
        _d(
            "Search index disk fills; admins delete files manually each week.",
            (
                "Relocate or expand index storage per Esri guidance and plan capacity—not repeated manual file deletes.",
                "Move search index to a network share without updating the index path in Portal settings.",
                "Truncate the index manually each week and assume Portal rebuilds missing entries on demand.",
                "Compress index files weekly and rely on manual compression as the long-term space strategy.",
            ),
        ),
        _d(
            "Backup retention is 14 days; audit requires 90-day recovery for a compliance app.",
            (
                "Align retention, immutability, and DR tooling with the compliance requirement; technical limits must match policy.",
                "Keep 14-day backups and supplement with manual exports when auditors request older data.",
                "Extend retention to 90 days on the same SAN as production without offsite copies.",
                "Rely on application-consistent VM snapshots for the geodatabase instead of SQL backups.",
            ),
        ),
    ]
    rows = []
    for issue in issues:
        stem, a, b, c, d = issue
        for t in tags:
            rows.append(
                _d(
                    "[Maint wave {t}] ".format(t=t + 1) + stem,
                    a,
                    b,
                    c,
                    d,
                )
            )
    return [("maintain-support-enterprise",) + x for x in rows]


def _manage_block():
    """104 manage: AD, LDAP, groups, enterprise logins, OAuth apps, sharing."""
    tags = list(range(8))
    idps = _IDPS
    issues = [
        _d(
            "Portal groups are linked to AD security groups, but removals in AD are slow to reflect in portal membership.",
            (
                "Verify group sync schedules, connectors, and that expectations match periodic sync—not always instantaneous removal.",
                "Force a manual portal group sync immediately after every AD change as standard procedure.",
                "Shorten the sync interval to 1 minute and assume portal handles the increased load.",
                "Remove members manually after each AD change and disable group-sync to avoid confusion.",
            ),
        ),
        _d(
            "LDAP group filters are too broad and grant publisher to unintended contractors.",
            (
                "Tighten LDAP queries and map groups to curated portal groups with explicit role assignments.",
                "Broaden the LDAP filter further to include all OU members and use custom roles to restrict.",
                "Assign Publisher to the contractor group and rely on content-level permissions only.",
                "Switch to manual group membership and skip LDAP sync for contractor groups.",
            ),
        ),
        _d(
            "Two IdPs map the same NameID to different people after a merger; content ownership is ambiguous.",
            (
                "Coordinate IdP attribute strategy and portal login rules so NameID is unique and stable across directories.",
                "Re-map all enterprise logins to a single IdP and assume NameID collisions auto-resolve.",
                "Concatenate both domain UPNs as NameID and rely on portal to deduplicate ownership.",
                "Set NameID format to email and assume both directories issue globally unique addresses.",
            ),
        ),
        _d(
            "OAuth confidential app client secret rotated; scheduled scripts still use the old secret.",
            (
                "Update stored secrets in secure automation and rotate connectors; scripts need the new credentials.",
                "Re-use the old secret in scripts until the next scheduled rotation window.",
                "Store the new secret in a shared config file accessible by all automation accounts.",
            "Extend token lifetime to 30 days so secret rotation frequency can be reduced.",
            ),
        ),
        _d(
            "Org policy forbids sharing to Everyone; a team publishes a public dashboard by sharing to a world-facing group.",
            (
                "Align sharing with governance; 'public' still means controlled visibility and compliance review—not bypassing org policy with workarounds.",
                "Share to a named external group and classify it as internal to satisfy the policy check.",
                "Request a policy exception and publish while the exception is pending approval.",
                "Grant the team Owner role so they can override sharing restrictions without admin review.",
            ),
        ),
        _d(
            "Service account for DB registration is correct, but DBAs renamed the instance; services fail authentication.",
            (
                "Update connection strings/registrations and SPNs as needed so the service account matches the new SQL endpoint.",
                "Update only the Portal data store registration and assume Server picks up the new instance name.",
                "Change the service account password as part of the rename remediation without updating SPNs.",
                "Re-register the database using a new service account and retire the old one without updating SPNs.",
            ),
        ),
        _d(
            "WFS is enabled; stakeholders believe the map is read-only because the app hides export.",
            (
                "Review OGC and REST capabilities versus sensitivity; UX hiding does not equal protocol-level read-only.",
                "Disable WFS and re-enable only when stakeholders explicitly request read-only exports.",
                "Set the WFS endpoint to return only geometry and omit attribute fields for all layers.",
                "Mark the layer as sensitive and rely on WFS schema complexity to deter extraction.",
            ),
        ),
        _d(
            "Contractors use enterprise logins; offboarding in AD is delayed by HR.",
            (
                "Use portal-side disables, group removal, and monitoring for high-risk items—not only AD timing.",
                "Wait for AD offboarding to complete before taking any portal-side action.",
                "Remove the contractor from the LDAP filter only and rely on the next sync to update portal.",
                "Change the portal sign-in page URL so contractor bookmarks no longer resolve.",
            ),
        ),
        _d(
            "Multiple OAuth redirect URIs are registered; dev and prod clients collide on the same client ID.",
            (
                "Separate apps or clearly scoped registrations per environment; redirect URI discipline prevents cross-environment token mix-ups.",
                "Register a single app with wildcard redirect URIs to cover all environments.",
                "Add both dev and prod redirect URIs to the same app and rely on client state parameters.",
                "Use the same client secret across environments and rotate only when a breach is suspected.",
            ),
        ),
        _d(
            "Collaboration workspace shows items but edits do not sync to the partner org.",
            (
                "Check sync direction, schedules, and supported content types for the collaboration—not only initial connection success.",
                "Verify that the collaboration workspace has the sending org listed as the access org.",
                "Re-send the collaboration invitation and assume the sync resumes automatically.",
                "Increase the sync schedule frequency to 5 minutes and assume items will appear.",
            ),
        ),
        _d(
            "Group owner departure locks administrative updates to a critical shared update group.",
            (
                "Transfer group ownership and content per policy before account deletion; plan for succession.",
                "Escalate to Esri support to unlock the group after the owner account is deleted.",
                "Re-create the group with a generic admin account and migrate members manually.",
                "Grant all members Update access as a workaround until a new owner is assigned.",
            ),
        ),
        _d(
            "Credits or premium tools spike; everyone has the same custom role.",
            (
                "Tighten privileges, assign tools by role, and monitor usage; least privilege limits cost and risk.",
                "Assign GeoAnalytics to all GIS Professional users and rely on usage reports to identify abuse.",
                "Enable credit budgets per user and assume the portal blocks usage automatically at the limit.",
                "Remove premium tool access from all users and require a manual request to re-enable.",
            ),
        ),
        _d(
            "AD UPN changes for a user; portal shows duplicate identities or broken ownership references.",
            (
                "Plan UPN changes with IdP and portal attribute mapping; identifiers tied to login must be managed deliberately.",
                "Update the portal username manually for each affected user without IdP coordination.",
                "Re-invite affected users under new UPNs and transfer content item by item.",
                "Change enterprise login usernames in portal to match new UPNs without IdP attribute update.",
            ),
        ),
    ]
    rows = []
    for issue in issues:
        stem, a, b, c, d = issue
        for t in tags:
            rows.append(
                _d(
                    "[Org {idp} policy {t}] ".format(idp=idps[t % len(idps)], t=t + 1) + stem,
                    a,
                    b,
                    c,
                    d,
                )
            )
    return [("manage-content-users",) + x for x in rows]


def get_extra_400_scenarios():
    """
    Returns list of 400 tuples: (domainId, stem, correct, w1, w2, w3).
    """
    deploy = []
    deploy.extend(_deploy_sso_block())
    deploy.extend(_deploy_cache_3d_block())
    deploy.extend(_deploy_fed_ssl_block())
    deploy.extend(_deploy_general_block())
    ts = _troubleshoot_block()
    mt = _maintain_block()
    mg = _manage_block()
    all_rows = deploy + ts + mt + mg
    assert len(deploy) == 136, len(deploy)
    assert len(ts) == 72, len(ts)
    assert len(mt) == 88, len(mt)
    assert len(mg) == 104, len(mg)
    assert len(all_rows) == 400
    return all_rows


if __name__ == "__main__":
    from collections import Counter

    c = Counter(x[0] for x in get_extra_400_scenarios())
    print(c)
    print("total", sum(c.values()))
