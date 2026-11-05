# Identifying and Blocking Traffic Anomalies in Cloudflare

## Objective

Enable consistent and prompt responses to traffic anomalies by implementing
procedures for identifying and blocking suspicious traffic—high request rates,
high error volume, or scraping patterns which disrupt service—in Openverse.

## When to use this runbook

Use this runbook when there is a marked increase in traffic visible in our AWS
dashboards or Cloudflare analytics and either of these are true:

1. There is a service disruption to the Openverse API or frontend.
2. There is a marked increase in resource usage on the API or frontend ECS
   services that continues to trend to unsustainable levels, which _could lead_
   to a service disruption.

## Requirements

1. Access to the Openverse Cloudflare dashboard.
2. Familiarity with the Cloudflare web UI, including the Analytics, Security,
   and Web Access Firewall tabs.
3. Time. This is an exploratory process that can take significant trial-and
   error.

## Procedure Steps

### 1. Identify the timeframe of the traffic anomalies

1.  Log into Cloudflare.
2.  Select the relevant domain in the Cloudflare UI.
3.  Go to `Analytics & Logs => Traffic` and choose the "Page Views" box in the
    left sidebar. You should see a page like the one shown in the image below.
    ![Cloudflare's Analytics & Logs => Traffic page sample](./cloudflare_traffic_ui.png)
4.  Set the time range dropdown to 24 hours.
5.  See if you can find the point where the current spike in traffic begins.
6.  If you do not see a place where traffic stabilizes to a relatively flat
    line, continue increasing the time range in the dropdown.
7.  Once you find where normalized traffic starts to spike in the graph, hover
    over the graph and **record the date and time the spike began**.

### 2. Identify targetable sources of the suspicious traffic

Next, we need to associate the traffic with specific sources. Essentially, we're
trying to find unique identifiers linked to potentially malicious traffic, so we
can block them through the Cloudflare Web Access firewall.

There are three primary identifiers for targeting traffic. These are ordered
from largest, most persistent, and most impactful, to smallest and most
ephemeral. When possible, **blocking Autonomous System Numbers (ASNs)** is the
single best way to mitigate malicious traffic.

#### Traffic Source Identifiers

```{note}
Expectations about the ratio of traffic a single source should occupy are based
on historical data and subject to change over time. To validate these baseline
percentages, please analyze a time-slice of traffic *without* any known
malicious traffic, if one exists in Cloudflare's available data, checking for
any single source exceeding the percentages listed here.
```

- Source "Autonomous System Numbers" (ASNs): Unique identifiers for a group of
  IP networks and routers under the control of a single organization, typically
  an internet service provider or hosting company.

  A single ASN usually makes up less than 10% of total Openverse requests in a
  given timeframe. If the percentage of requests from a single ASN is
  significantly higher than 10%, it may indicate that one or more users on the
  ASN are scraping Openverse or over using/abusing expected programmatic access
  patterns.

- Source user agents: Unique user-agent strings sent with requests to Openverse.
  Nearly all UA strings from web browsers begin with `Mozilla`. Outside of the
  latest stable version of Chrome on Windows 10, which is the most popular
  Openverse browser (and usually looks something like
  `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{webkit-version} (KHTML, like Gecko) Chrome/{real-chrome-version} Safari/{webkit-version}`),
  no single user agent should take up more than 10% of total traffic. Excluding
  these with a `Source user agent does not contain Mozilla` or
  `Source browser equals Unknown` filter in the analytics UI can reveal other
  user agents from things like social media platforms and popular http request
  software libraries, like `Go-http-client/2.0` or `axios/0.21.4`, as examples.

- IP addresses: A unique identifier for a single machine or user.

  Typically, a single IP address makes up less than 1% of total Openverse
  requests in a given timeframe. Larger IPs which exceed this 1% figure
  typically belong to "good" web crawlers from places like Google, Bing, and
  Dotbot, as examples. Traffic exceeding 1% which isn't from one of these
  crawlers could suggest that a user on the ASN is scraping Openverse or
  accessing Openverse programmatically in an aggressive way.

#### Steps

1.  Using
    [the view from the previous task](#1-identify-the-timeframe-of-the-traffic-anomalies),
    scroll down and look for IP Addresses, Source ASNs, or Source User Agents
    which exceed the typical usage thresholds defined above. Create a list of
    these traffic sources.

```{note}
Cloudflare will only show the 5 largest of each category; greater than 5
disproportionately-large items of any category would be unprecedented and
surprising in Openverse's history.
```

```{warning}
If you haven't found anything, it's unlikely that this situation is connected
to malicious traffic or specific actors. Instead, it is more likely to be a
normal increase in traffic to Openverse. At this point, it's more likely that a
change in code or infrastructure has caused a performance drop, exposed by the
higher traffic, or that the traffic has grown so much that we need to allocate
additional server resources. Consider recent Openverse marketing efforts or
WordPress events if the traffic looks organic and we need to attribute it to
something.
```

2.  Take the list of suspicious traffic source IDs and go to the
    `Security => Bots` section of Cloudflare. Here, you'll see more lists of IP
    Addresses, ASNs, and User Agents below a graph of known bot traffic. It is
    likely you'll see items from your lists in these graphs.

3.  Use the "add filter" button and filter by your listed resources
    individually. Write down which of the identified resources are comprised of
    the most `Automated` and `Likely Automated` traffic.

```{warning}
If an ASN has a significant amount of human traffic, it can indicate this ASN
is an ISP rather than a hosting company or company which offers a Virtual
Private Network. Blocking these types of ASNs can disrupt service to human users.
```

### 3. Block suspicious traffic sources in the Web Access Firewall

For each source in your list, create a **Web Access Firewall rule** in
Cloudflare. These can be found in the `Security => WAF` section. The
[official Cloudflare docs](https://developers.cloudflare.com/firewall/cf-dashboard/create-edit-delete-rules/#create-a-firewall-rule)
explain how to do this well. Some suggestions:

- Add the type of source being blocked to the name of the rule in brackets. For
  example, we currently use a `[bot-asn]` name prefix for all rules relating to
  ASNs.
- When writing rules which match ASNs, only the 5-digit number of the ASN is
  used in the rule. For this reason, it's nice to add the name of the ASN to the
  rule name as well. For example, rule name `[bot-asn] ZackWorld` which blocks
  ASN `13335`.
- Default to the "Block" action for each firewall rule.
- If a source id had a high percentage of human traffic and is making requests
  to the frontend, but you still feel it should be blocked, consider using the
  "Managed Challenge" action instead of an outright block. This should allow
  human users but block automated traffic.

### 4. Analyze reputation of identified traffic sources

Finally, make a web search in your preferred browser for each individual traffic
source identifier. Many ASNs and IP addresses used for scraping will have
negative reports, be on spam lists, or be associated with hosted VPN services.
This can be helpful in identifying which are truly malicious.

### 5. Monitor and Adjust Blocking Rules

Periodically in the days after using this runbook repeat the entire process, at
your discretion, only continuing if new sources of traffic have appeared. When
blocking ASNs, it is unlikely that a scraping network, for example, would switch
regions or hosting companies. If new IPs with disproportionate traffic appear
and a similar traffic anomaly is present, this may suggest a botnet that hasn't
been appropriately targeted. Try to find an ASN or UA that matches the new IPs,
and can be correlated to the traffic from the original incident. Any targetable
property which they share in common could be a great block target.

## Escalation Procedures

1. If the team member is unable to complete the procedure successfully, escalate
   the issue to the rest of the team via a ping in our team chat. A maintainer
   should review your run of the book and repeat it if they find a particular
   type of traffic anomaly wasn't assessed.
2. Here we will explore more drastic measures for mitigating the service
   disruption, like API throttling or rate limiting adjustments.
