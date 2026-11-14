# Incident Response Runbook

```{note}
**Recording** an incident is a standalone task which can be performed by any maintainer. This recorder is not necessarily the one to stabilize the service or continue to work on incident triage.
```

```{warning}
This runbook is intended to be used by Openverse maintainers, and references some resources that only Openverse staff have access to.
```

## 1. Record the incident

When you observe a potential incident, you are responsible for recording it. Run
the `/Incident Report` command in the maintainer’s `#openverse` Slack channel.
This command will prompt for some basic information about the incident and then
guide you into creating an incident report in the maintainer P2 blog.

The command can also be run with a bookmarked "Report an Incident" link inside
of Slack, which is found at the top of all `#openverse-` maintainer channels.

### Determining an estimated severity

You will be asked to provide an estimated
[severity](/meta/incidents/index.md#severity) for the incident. You are expected
to use your best judgement here, but here are some examples to help you:

- **Severity 1** examples:
  - <https://openverse.org> is completely down.
  - Frontend searches aren't returning any results
  - The API is serving error codes for all searches
- **Severity 2** examples:
  - Frontend keyboard navigation is broken
  - A particular provider with ~1.5m images is not returning any API results
  - Users based in the UK, comprising 6% of all visitors, are unable to view
    <https://openverse.org>
- **Severity 3** examples:
  - A piece of our staging infrastructure has completely failed.
  - A staging site is down
  - Greek frontend translations are not displaying, instead falling back to
    English

### Concluding Reporting

Monitor the incident until a lead has been identified. This will be the MSR, by
default or another online member of the team (perhaps even yourself). At this
point, reporting the incident is complete.

## 2. Stabilize service

1. Complete any necessary communication work. For Severity 1, this means
   messaging the maintainers via Signal that an outage is occurring. Depending
   on the severity, a Make post announcing that the outage is being investigated
   may also be warranted.
   1. If the incident was discovered by a user in a communication channel,
      please reply to them, and thank them for their report. Let them know the
      team is investigating the issue.
2. The point person should always have an up-to-date understanding of the
   situation. Post updates to P2 regularly depending on severity (ideally hourly
   for severity 1, but daily or otherwise for severity >= 2). Anyone who signs
   on for the day while the incident is being triaged should jump into
   stabilizing the service with the team. Be proactive! Ask how you can help.
3. Perform any necessary tasks to triage/mitigate the incident. Delegate what
   you can to online developers. It is assumed that anyone online can and will
   help, and that incidents take precedence over regular work. Some tips for
   triaging:
   1. It’s possible we have an existing runbook related to the type of incident
      you’re dealing with, particularly if it was triggered by a monitoring
      alarm. Search the
      [runbook documentation](/meta/monitoring/runbooks/index.md) for useful
      information.
      1. Understanding [service deployment mechanisms](/general/deployment.md)
         will likely be useful.
      2. Traffic anomalies? See
         [this guide](/meta/monitoring/traffic/runbooks/identifying-and-blocking-traffic-anomalies.md)
         for suggestions.
   2. Be prepared to check logs in AWS, observe traffic in Cloudflare, and look
      at dashboards for information on server resources. A useful guide on logs
      [can be found here](/meta/monitoring/cloudwatch_logs/index.md).
   3. Checking for differences between staging and production can also be
      illuminating.
   4. Record _everything_. Keep a local file as a scratchpad for notes, post
      them to the Slack thread. The more retained raw information the better.
      Before deleting or restarting anything: make backups, take screenshots or
      copy/paste important text wherever you can.
   5. If something is related to a 3rd party API, like a provider or SaaS
      offering used in Openverse, contact them as soon as possible.
   6. Start a Slack huddle if real time audio or video would be useful.
   7. For incidents that may last several hours, consider silencing any AWS
      alarms that are actively being investigated - the extra noise can distract
      and detract from the stabilization work. For any AWS alarms, this can be
      done by setting the "Alarm action" to "Disabled" in the AWS UI.
4. When the service has become stable again, update the status tag of the P2 to
   `#status-stabilized` and leave a comment summarizing the mitigation. Usually
   at this time the urgency of the incident will be reduced, and time may be
   required to observe that the incident is fully resolved.

```{note}
Once services are stabilized, the urgency of the incident is usually reduced. The next steps can happen asynchronously and with priority commenserate to incident severity.
```

## 3. Investigate or resolve

Depending on the nature of the incident, services may be stable but require
further investigation into a root cause. If a root cause is already known,
resolved, or no additional action can/should be taken, the incident can be
marked as resolved.

**Investigating**:

1. If more investigation is required, update the status tag of the P2 to
   `#status-investigating`. Share the outcome of the investigation in the P2 and
   any issues that were created as a result of it.
2. Prioritize the work on the created issues alongside existing workstreams, and
   complete as appropriate.
3. Once the related issues are complete, move on to resolving the incident.

**Resolving**:

1. Once enough time has passed without disturbance that the incident seems
   resolved, update the status tag of the P2 to `#status-resolved`, leave a P2
   comment summarizing the solution, adding any relevant points to the timeline,
   and unpin the Slack thread. Re-enable any alarms that were disabled.
2. Update all communication postings, editing them so that the incident is
   clearly resolved in the title and body of the post. This includes the Make
   post for Severity 1 incidents along with any other outreach.

## 4. Review the incident

Once the incident is resolved, the point person should host a retrospective as
soon as possible. The closer to the actual incident, the better. Make sure
everyone relevant attends, including anyone who recorded or helped triage the
incident. Postmortems should be blameless, and we typically use the
["5 Whys?"](https://www.mindtools.com/a3mi00v/5-whys) method to identify root
causes of the incident and/or gaps in the incident response process.
[Here is a recent example.](https://docs.google.com/document/d/1VGCWR85ipt_grLbDu_mKN31RAPTNEL_emvqDj1vcg20/edit)
The postmortem process should generate action items and follow-up work that must
be managed and prioritized appropriately. The team may not have capacity to
perform a postmortem on each incident, but should do so for any incident that is
particularly severe or has a high likelihood of recurrence. Once a postmortem
has been completed, the status tag of the P2 should be updated to
`#status-reviewed`.
