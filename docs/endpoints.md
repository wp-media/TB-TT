# Tech Team Bot API Endpoints

This document describes the available API endpoints and Slack commands for the Tech Team Bot.

## Support Endpoints

The support endpoints provide access to IP address information for WP Rocket services. These endpoints are used by the support team to retrieve IP addresses for firewall configuration and troubleshooting purposes.

### Base URL

All support endpoints are prefixed with `/support`

### Endpoints

#### 1. Get WP Rocket IPs (Human Readable)

Returns a human-readable list of all IP addresses used by WP Rocket services, including CloudFlare proxy IPs and group.One infrastructure IPs.

**Endpoint:** `/support/wprocket-ips`

**Method:** `GET`

**Authentication:** None required

**Response Format:** Plain text

**Response Example:**

```
List of IPs used for WP Rocket:

License validation/activation, update check, plugin information:
https://wp-rocket.me
173.245.48.0/20
103.21.244.0/22
[CloudFlare IPv4 and IPv6 ranges...]

Load CSS Asynchronously:
https://cpcss.wp-rocket.me
46.30.211.168
46.30.212.76
[group.One IPs...]
2a02:2350:4:200::/55

Remove Unused CSS:
46.30.211.168
[group.One IPs...]
User Agents:
WP-Rocket/SaaS Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36...

Dynamic exclusions and inclusions:
https://b.rucss.wp-rocket.me
[group.One IPs...]

RocketCDN subscription:
https://rocketcdn.me/api/
[group.One IPs...]
```

**Use Case:**

- Support team reference documentation
- Manual firewall configuration
- Troubleshooting connectivity issues

---

#### 2. Get WP Rocket IPv4 (Machine Readable)

Returns a machine-readable list of all IPv4 addresses used by WP Rocket services. One IP per line, no descriptive text, with duplicates removed.

**Endpoint:** `/support/wprocket-ips/ipv4`

**Method:** `GET`

**Authentication:** None required

**Response Format:** Plain text (one IP per line)

**Response Example:**

```
173.245.48.0/20
103.21.244.0/22
46.30.211.168
46.30.212.76
46.30.212.77
5.249.224.8
5.249.224.9
```

**Use Case:**

- Automated firewall rule generation
- Scripted IP whitelisting
- Integration with security tools

---

#### 3. Get WP Rocket IPv6 (Machine Readable)

Returns a machine-readable list of all IPv6 addresses used by WP Rocket services. One IP per line, no descriptive text, with duplicates removed.

**Endpoint:** `/support/wprocket-ips/ipv6`

**Method:** `GET`

**Authentication:** None required

**Response Format:** Plain text (one IP per line)

**Response Example:**

```
2400:cb00::/32
2606:4700::/32
2a02:2350:4:200::/55
```

**Use Case:**

- Automated firewall rule generation for IPv6
- Scripted IP whitelisting for IPv6
- Integration with security tools

---

## Site Monitoring

TB-TT monitors a set of WordPress test sites (one per hosting provider, e.g. one.com, Hostinger, WP Engine), each running the full plugin suite (WP Rocket, Imagify, BackWPUp, RankMath, etc.). A k8s CronJob calls TB-TT hourly per site; TB-TT runs health checks and a pending-updates check, then posts a summary to the `#wpmedia_auto-e2e-reports` Slack channel.

### Base URL

The site monitoring endpoint is prefixed with `/site-monitor`.

#### Check a site

**Endpoint:** `/site-monitor/check/<site_slug>`

**Method:** `POST`

**Authentication:** Required — `X-Api-Key` header, matching the `TBTT_API_KEY` app secret

**Response:** `202 {}` immediately. The checks run in a background thread; the actual result is posted to Slack (channel `auto-e2e-reports`), not returned in the HTTP response. `404` if `site_slug` is not a known site (see `config/wp-test-sites.json`), `401` if the API key is missing or wrong.

**Checks performed** (see `sources/factories/WordPressSiteFactory.py`):

- `homepage (cached)` and `homepage (uncached)` — homepage reachability, with the uncached variant bypassing WP Rocket's page cache via `?nowprocket` plus a cache-busting query param
- `login page` — `wp-login.php` reachability
- `REST API` — anonymous `GET /wp-json/` reachability
- `wp-admin (authenticated)` — authenticated `GET /wp-json/wp/v2/users/me` using the site's application password, exercising the full authenticated bootstrap (not just anonymous reachability)
- `pending updates` — calls the TB-TT Site Monitor WordPress plugin's `GET /wp-json/tbtt-monitor/v1/updates-pending` route to check for pending core/plugin/theme updates

Each check reports a `status` of `ok`, `warning`, or `fail`. Reachability check failures are always `fail`. A pending update is only ever a `warning` — WordPress's own auto-updates are expected to apply it in due course, and flagging it as a hard failure would raise false alarms (e.g. right after a site switches to WordPress Beta Tester's nightly core channel, there is almost always something "pending" between hourly runs). Only a broken call to the pending-updates route itself (e.g. the plugin got deactivated, so its REST route 404s) is a `fail`.

### Adding a new test site to the monitoring list

1. **Provision the WordPress site** on the target host, install the full plugin suite, and note its URL.
2. **Install the TB-TT Site Monitor plugin** (`wordpress-assets/tbtt-site-monitor/tbtt-site-monitor.php` in this repo) as a regular plugin on the site (`wp-content/plugins/tbtt-site-monitor/`) and activate it. It forces WP Rocket auto-updates on and exposes the pending-updates REST route.
3. **Install and activate the "WordPress Beta Tester" plugin** (`wordpress-beta-tester`) so the site tracks WordPress core's nightly channel — the TB-TT Site Monitor plugin selects the channel automatically once Beta Tester is active.
4. **Set `WP_AUTO_UPDATE_CORE = true`** in the site's `wp-config.php` so nightly core builds actually auto-apply unattended (Beta Tester only makes them available; this constant is what makes WordPress apply them on its own).
5. **Create an Application Password** for an admin user on the site (Users → Profile → Application Passwords in wp-admin).
6. **Add the hostname to the TB-TT k8s egress allowlist**: TB-TT's pods only have outbound network access to hosts explicitly allowed through the firewall. Order an egress rule for the new site's hostname via [chef-self-service.one.com/order/chef-repo/k8s-add-firewall-egress.rb](https://chef-self-service.one.com/order/chef-repo/k8s-add-firewall-egress.rb/) — without this, TB-TT's requests to the site will time out or be blocked even though everything else is configured correctly.
7. **Add the site to `config/wp-test-sites.json`**, following the existing entries:
   ```json
   "my-new-host": {
       "label": "My New Host",
       "url": "https://my-test-site.example.com",
       "app_user": "the-wp-admin-username",
       "app_password_env": "TBTT_SITE_MY_NEW_HOST_APP_PASSWORD"
   }
   ```
8. **Add the application password as a new secret**, `TBTT_SITE_MY_NEW_HOST_APP_PASSWORD` (matching `app_password_env` above), to the `tbtt-secrets` k8s secret used by the TB-TT deployment.
9. **Add the new site slug to the k8s CronJob** that triggers `/site-monitor/check/<site_slug>` hourly (the CronJob manifest is managed outside this repo) so the new site gets checked on the same schedule as the others.
10. **Verify**: `curl -X POST -H "X-Api-Key: <TBTT_API_KEY>" https://<tbtt-host>/site-monitor/check/my-new-host` and confirm a summary for the new site shows up in `#wpmedia_auto-e2e-reports`.

---

## Slack Commands

### `/wprocket-ips` Command

Sends a direct message to the requesting user with a human-readable list of all IP addresses used by WP Rocket services.

**Command:** `/wprocket-ips`

**Access:** Available to all Slack workspace members

**Response:** Direct message (DM) from the bot

**Response Content:** Same format as the `/support/wprocket-ips` endpoint

**Example Usage:**

1. User types `/wprocket-ips` in any Slack channel
2. Bot sends a DM to the user with the complete IP list
3. User can copy the information for firewall configuration or documentation

**Implementation Details:**

- Command is handled by `SlackCommandHandler.wp_rocket_ips_command_callback()`
- Processing runs in a separate thread to avoid blocking
- Uses `ServerListHandler.send_wp_rocket_ips_to_slack()` to generate and send the message
- Message includes:
  - CloudFlare proxy IPs (IPv4 and IPv6)
  - group.One infrastructure IPs (20 individual IPv4 addresses and IPv6 ranges)
  - User agent strings for WP Rocket SaaS services
  - Service-specific IP groupings with descriptive headers

---

## IP Address Sources

### CloudFlare IPs

- Fetched dynamically from `https://www.cloudflare.com/ips-v4/` and `https://www.cloudflare.com/ips-v6/`
- Updated in real-time when endpoints are called
- Used for services proxied through CloudFlare (e.g., wp-rocket.me)

### group.One IPs

- **IPv4:** 20 specific IP addresses provided by group.One Ops
  - Range: `46.30.211.x`, `46.30.212.x`, `5.249.224.x`
  - Used for: Load CSS Asynchronously, Remove Unused CSS, Dynamic exclusions, RocketCDN subscription
- **IPv6:** CIDR ranges from group.One infrastructure
  - `2a02:2350:4:200::/55` (k8spods CPH3)

**Note:** group.One IP addresses are hardcoded based on infrastructure configuration provided by group.One Ops. Contact group.One Ops for updates.

---

## Technical Architecture

### Module Structure

```
TechTeamBot (sources/TechTeamBot.py)
 __setup_support_enpoints()
     SupportListener (sources/listeners/SupportListener.py)
         ServerListHandler (sources/handlers/ServerListHandler.py)
             get_cloudflare_proxy_ipv4()
             get_cloudflare_proxy_ipv6()
             get_groupone_ipv4()
             get_groupone_ipv6()
             generate_wp_rocket_ips_human_readable()
             generate_wp_rocket_ipv4_machine_readable()
             generate_wp_rocket_ipv6_machine_readable()
```

### Error Handling

- **CloudFlare fetch errors:** Returns error message in response (e.g., "Error: Unable to reach CloudFlare")
- **Invalid requests:** Standard Flask error handling
- **Slack command errors:** Logged to application logs, user receives no response (Slack timeout)

---

## Maintenance

### Updating group.One IPs

To update the group.One IP addresses:

1. Obtain the updated IP list from group.One Ops
2. Update the `group_one_ips` list in `sources/handlers/ServerListHandler.py:get_groupone_ipv4()`
3. Run tests: `docker-compose exec -T web python -m pytest tests/unit/ServerListHandlerTest.py`
4. Deploy the updated code

### Monitoring

- All endpoint calls are logged to the application logs
- CloudFlare IP fetch failures are logged with error details
- Slack command processing is logged with thread start information

---
