# Incident Response Runbook

1.  **Identify and Record the incident.** When you observe an incident, you are
    responsible for recording it following these steps:
1.  Run the `/Incident Report` command in the maintainer’s #openverse Slack
    channel. This command will create a Slack alert message and provide you with
    instructions for next steps. Those steps will look something like this:
    1. Create a post on the internal maintainer P2 blog using the "Incident"
       template. Fill in the blank information and publish.
1.  If the incident has any clear relationship to the code, create a critical
    GitHub issue for the incident.
1.  Now, continue to monitor the incident until a point person has been
    identified. Either the MSR by default or another online member of the team.
    At this point, reporting the incident is complete.
1.  **Resolve the incident.** Hello, point person. It’s time to begin triaging
    the incident.

    1.  Complete any necessary comms work. For Severity 1 and 2 incidents, this
        means a Make post announcing the outage is being investigated.
        1. If the incident was discovered by a user in a communication channel,
           please reply to them and thank them for their report. Let them know
           the team is investigating the issue.
    2.  The point person should always have an up-to-date understanding of the
        situation. Post updates to P2 hourly*.* Anyone who signs on for the day
        while the incident is being triaged should jump into resolving the issue
        with the team. Be proactive! Ask how you can help.
    3.  Perform any necessary tasks to triage the incident. Delegate what you
        can to online developers. It is assumed that anyone online can and will
        help, and that incidents take precedence over regular work. Some tips
        for triaging:
        1. It’s possible we have an existing runbook related to the type of
           incident you’re dealing with. Search
           the[docs](https://docs.openverse.org/) for useful information.
           1. Understanding[deploys](https://docs.openverse.org/general/deployment.html)
              will likely be useful.
           2. Traffic anomalies?
              See[this guide](https://docs.openverse.org/meta/traffic/runbooks/identifying-and-blocking-traffic-anomalies.html)for
              suggestions
        2. Be prepared to check logs in AWS, observe traffic in Cloudflare, and
           look at dashboards for information on server resources.
        3. Checking for differences between staging and production can also be
           illuminating.
        4. Record _everything_. Keep a local file as a scratchpad for notes,
           post them to the Slack thread. The more retained raw information the
           better. Before deleting, or restarting anything, take screenshots or
           copy/paste important text wherever you can.
        5. If something is related to a 3rd party API, like a provider or SaaS
           offering used in Openverse, contact them as soon as possible.
        6. Start a Slack huddle if real time audio would be useful.
    4.  When the incident seems resolved, update the status of the P2 page as
        "Resolved", leave a P2 comment summarizing the solution, and unpin the
        Slack thread.
    5.  Update all comms postings, editing them so that the incident is clearly
        resolved in the title and body of the post. This includes the Make post
        for Severity 1 and 2 incidents along with any other outreach.
    6.  Create any follow-up issues, with a GitHub project if extensive. This
        can be done the next time you are online if you have been working for an
        extended period or outside of your regular work hours.

1.  **Review the incident.** Once the incident is resolved, the point person
    should host a retrospective as soon as possible. The closer to the actual
    incident, the better. Make sure everyone relevant attends, including anyone
    who recorded or helped triage the incident. Postmortems should be blameless
    and we typically use the "5 Whys?"" method to identify root causes of the
    incident and/or gaps in the incident response process.
    [Here is a recent example.](https://docs.google.com/document/d/1VGCWR85ipt_grLbDu_mKN31RAPTNEL_emvqDj1vcg20/edit)
    The postmortem process should generate action items and follow-up work that
    must be managed and prioritized appropriately.
