# 2024-01-05 Implementation Plan: Finish moving all services to `openverse.org`

**Author**: @sarayourfriend

<!-- See the implementation plan guide for more information: https://github.com/WordPress/openverse/tree/19791f51c063d0979112f4b9f4eeace04c8cf5ff/docs/projects#implementation-plans-status-in-rfc -->
<!-- This template is exhaustive and may include sections which aren't relevant to your project. Feel free to remove any sections which would not be useful to have. -->

## Reviewers

<!-- Choose two people at your discretion who make sense to review this based on their existing expertise. Check in to make sure folks aren't currently reviewing more than one other proposal or RFC. -->

- [x] @AetherUnbound
- [x] @dhruvkb

## Project links

<!-- Enumerate any references to other documents/pages, including milestones and other plans -->

- [Project Thread](https://github.com/WordPress/openverse/issues/2037)

This project does not have a project proposal because the scope and rationale of
the project are clear, as defined in the project thread. I've clarified these
expectations in the [expected outcomes](#expected-outcomes) section below.

## Overview

<!-- An overview of the implementation plan, if necessary. Save any specific steps for the section(s) below. -->

Openverse's Airflow instance and Django API both live on `openverse.engineering`
and must be moved to `openverse.org` in order to downgrade our Cloudflare plan
for `openverse.engineering`. A number of supporting services expect these
services to be there. Moving the Airflow instance is relatively trivial compared
to moving the API, primarily because Airflow has no external dependents (only
Openverse maintainers use it) and thus does not need redirects. Nor is it
subject to zero-downtime deployment requirements like the API.

This plan is split into two major parts:

1. [Move Airflow to `airflow.openverse.org`](#1-move-airflow-to-airflowopenverseorg)
2. [Move the Django API to `api.openverse.org` (with staging at `api-staging.openverse.org`)](#2-move-the-django-api-to-apiopenverseorg)

There are also two supplemental parts, a [preliminary step](#0-preliminary-work)
and a
[finalisation step](#3-update-references-announce-to-make-blog-and-finalise).

## Expected Outcomes

<!-- List any succinct expected products from this implementation plan. -->

- `openverse.engineering` should move to the Cloudflare free tier
- All services should live on `openverse.org`
- Production API domains on `openverse.engineering` should redirect to
  `openverse.org`

## Step-by-step plan

<!--
List the ordered steps of the plan in the form of imperative-tone issue titles.

The goal of this section is to give a high-level view of the order of implementation any relationships like
blockages or other dependencies that exist between steps of the plan. Link each step to the step description
in the following section.

If special deployments are required between steps, explicitly note them here. Additionally, highlight key
milestones like when a feature flag could be made available in a particular environment.
-->

### 0. Preliminary work

1. Move the `access` module that configures Cloudflare Access to a new
   `cloudflare` root module, maintaining the existing configuration.
   [The rationale for the new root module is explained in this section](#moving-cloudflare-access-and-the-new-cloudflare-root-module).
1. Rename the `org` root module to `github`.
1. Extract load balancer listener rules out of `generic/service` and
   `generic/ec2-service` in favour of a more generic form of the existing
   `service-alias` called `service-domain` (effects all existing services in the
   `next` root modules that have external domains). Update all existing services
   to use this new `service-domain` module for all domains associated with them.
1. Similarly, extract security group configuration out of `generic/service` and
   `generic/ec2-service` into a new module, `generic/security-group`. The new
   module will configure a default security group with strict access based on
   our load balancer and SSH-bastion entrypoints for HTTP(S) and SSH
   respectively. As with the previous point, this deduplicates near identical
   configuration in `generic/service` and `generic/ec2-service`.
1. Remove `register_with_target_group` option from `ec2-service` to simplify the
   module. Registration must be handled using Ansible playbooks for these
   services, so the updated module should never register the instance to the
   target group.

### 1. Move Airflow to `airflow.openverse.org`

1. Add `airflow.openverse.org` to Cloudflare access.
1. Create a new `airflow` module in the `next` root module. Use `ec2-service` as
   the basis with Ansible used to configure the service (compose file, settings,
   and cron job), to start the service, and to register it with the target
   group.
1. Spin down the existing Airflow EC2 service to prevent any potential issues
   with multiple running instances.
1. Deploy the `next` Airflow module and use the new `service-domain` to point
   `airflow.openverse.org` to the new service.
1. Port all Airflow Cloudflare rules from `openverse.engineering` to
   `openverse.org`.
1. Validate the new Airflow service:
   - Stop the existing service
   - Run provider DAGs and data refresh from the new service
   - Debug issues
   - Decommission the old service and remove all supports for it from Cloudflare
     (rules, Access, etc)

### 2. Move the Django API to `api.openverse.org`

The general idea for this set of changes is to leverage the fact that both
`openverse.engineering` and `openverse.org` can point to the external load
balancer, and the load balancer can freely discriminate between requests for
each host and direct requests wherever it wants, with listeners ordered in
arbitrary priority. That means all the API needs, at the most basic level, is to
have new CNAME records in Cloudflare added to point `api.openverse.org` to the
load balancer, and new load balancer listener rules to forward those requests to
the existing API services. By itself, that would indeed make the API accessible
on `openverse.org`. However, it would leave all the Cloudflare configuration for
the API on `openverse.engineering` inoperable for `openverse.org` (because these
rules are per-zone). So, the rest of the steps in this section are aimed at
carefully preparing and moving the service's Cloudflare configuration to
`openverse.org`.

```{note}
I am using `api(-(production|staging))?.` as shorthand for the three subdomains used
for our staging and production API. For clarity, this should be understood to expand to:
- `api.`
- `api-production.`
- `api-staging.`
```

1. Add `api(-(production|staging))?.openverse.org/admin` to Cloudflare Access
   and duplicate all API Cloudflare rules from `openverse.engineering` to
   `openverse.org`.
   - [This must all be in the `cloudflare` root module](#moving-cloudflare-access-and-the-new-cloudflare-root-module).
1. Add `api(-(production|staging))?.openverse.org` to `domain_aliases` for the
   API services and use a new `generic/service-domain` to point
   `api(-(production|staging))?.openverse.org` to the existing API services.
   - Rule priority does not matter here because our rules match on the requested
     host name, so the `openverse.org` and `openverse.engineering` listeners
     will never interrupt each other.
1. Redirect `api(-production)?.openverse.engineering` to `api.openverse.org`
   using a Cloudflare
   [dynamic single redirect rule](https://developers.cloudflare.com/rules/url-forwarding/single-redirects/)
   that matches only when a special header is present for testing.
   - Configure this in
     [the `cloudflare` root module](#moving-cloudflare-access-and-the-new-cloudflare-root-module),
     not in the environment root modules.
   - We will redirect both `api.openverse.engineering` and
     `api-production.openverse.engineering` to `api.openverse.org`. This reduces
     the complexity of the dynamic target expression.
   - We will not redirect staging. Staging has no guarantees for users.
     Excluding it from the redirects also reduces the overall complexity of both
     the redirect match and dynamic target expressions.
1. Update UptimeRobot monitors to point to the `openverse.org` domains.
1. **Production only steps**
   1. Update the frontend to point to `api.openverse.org` (only possible after
      configuring the domain for the production API because the staging and
      production frontend both point to the production API).
   1. Open PRs in Gutenberg and Jetpack to update the Openverse integration URL
      to `api.openverse.org`
   1. Create and run a management command to run in production that emails
      registered production API users to notify them of the change to
      `api.openverse.org`. Make it absolutely clear the old URL will redirect
      from the old domain to prevent anyone from panicking that their
      integration will break.
   1. On the rollout date specified in the message from the previous step,
      remove the special header condition of the redirect listeners so that all
      requests to the old production API domains redirect to
      `api.openverse.org`.
      - I suggest 2 weeks from the day we send the emails.
1. For Cloudflare redirect rules to work, we need to maintain a DNS record on
   each subdomain that is redirected. Replace Cloudflare DNS records for
   `api(-production)?.openverse.engineering` domains with noops, configured in
   the `cloudflare` root module. In doing this, we'll need to immediately remove
   the `generic/service-domain` instances pointing those domains to the load
   balancer, otherwise the next root module will overwrite the new settings.
   - After this, control over requests to `openverse.engineering` API domains
     will rest solely with the Cloudflare redirect rule, and forwarded to the
     appropriate `openverse.org`.
1. Remove Cloudflare configuration for `openverse.engineering` API domains from
   rules and Access. This will require manually deleting resources in the
   Cloudflare dashboard, as well as changes to the `cloudflare` root module (for
   Access).

### 3. Update references, announce to Make Blog, and finalise

1. Update references to `openverse.engineering` domains in our public and
   internal documentation to use `openverse.org` instead.
1. Publish a Make blog post announcing the change.
1. Decomission all resources from `openverse.engineering` except the redirect
   rule. At this point, I think we can also remove the
   `search.openverse.engineering` settings, as no one should be using it anymore
   and it was never a "public" access point for the Openverse frontend (we only
   used it in the iframe and never advertised it directly).
1. Downgrade `openverse.engineering` Cloudflare plan to the free tier.

## Step details

<!--
Describe all of the implementation steps listed in the "step-by-step plan" in detail.

For each step description, ensure the heading includes an obvious reference to the step as described in the
"step-by-step plan" section above.
-->

### Preliminary work

The first of these two steps are straightforward, with little possible
additional description to the tasks other than what I've written above. Instead,
I'll share the rationale for the changes here. I do so in order of complexity,
from least to most complex. I've added specific steps for the networking module
changes because those are more complex.

#### Moving Cloudflare Access and the new `cloudflare` root module

Moving the Cloudflare Access configuration out of the legacy root modules is
just one more step in our progress towards eliminating the legacy Terraform
configuration. There's nothing about the module that requires it to be in the
legacy root environments, so this should be a fairly easy one to move, but will
require importing resources into the new root module and using
`terraform state rm` to remove them from the legacy root module, in order to
prevent them from being deleted if the legacy root module is applied.

We'll move this to a new `cloudflare` root module rather than one of the `next`
environment root modules, because there is no specific environment related to
these settings, and it's best to keep these all together in a single place.
Later on, in the Airflow and API work, we'll expand the Cloudflare configuration
in `cloudflare` to include the Page, Cache, and WAF rules related to these
services that are currently configured by hand in the `openverse.engineering`
zone.

Cloudflare rules also have priority ordering, they are matched in a specific
order, and we need to be able to manage that ordering explicitly. We cannot
easily (reliably) configure environment-specific rules in a separate root
modules with priorities that reference the other environment's rules, at least
not without creating an artificial dependency between the two (like some shared
super-variable file the two reference to determine priority settings). It's much
easier to write and understand if the rules are all configured in the same
place, with priority settings that can explicitly reference each other within
the same module or even same file.

Using a separate root module also makes it possible to quickly iterate on
changes to the Cloudflare configuration in Terraform without introducing
dangling changes in the `next` root modules, which are more complex, and evolve
at a slower pacing than our Cloudflare configuration sometimes does. This will
make it possible to open PRs with changes to the Cloudflare configuration
recorded in Terraform, while reducing the chance that another change in
`next/production` (for example, where we might store these otherwise) could
overwrite them.

A potential alternative to using a new `cloudflare` root module to include these
in the `org` root module, which is separated from the `next` environment root
modules for similar reasons: the resources it configures are almost entirely
independent of our AWS infrastructure. That would be fine, in fact, except that
aside from the Cloudflare Access configuration, `org` is a strange name for the
place to store Cloudflare configurations, because they aren't related to
Openverse's organisational practices (again, aside from Cf Access). We could
rename `org` to something else, but I'm not sure what would include the GitHub
repository configuration and our Cloudflare configuration. I've thought about
this quite a bit and can't come up with a name that would be _more_ intuitive
than a separate `cloudflare` root module. If we do that, I would also like to
rename the `org` root module to `github`, and move the configuration in its
`github` child module into the root module.

This separation also moves things somewhat further in-line with recommendations
to have smaller root modules.
[This blog post describes an extreme version of this where each application is its own root module, and environment configuration differences are stored in `tfvars` files, rather than in the HCL itself](https://www.digitalocean.com/community/tutorial-series/how-to-manage-infrastructure-with-terraform).
I don't think we should move in that direction, mostly because I think our
current per-environment monolith works well, particularly because it makes sure
that the interconnected parts of our application do not drift, without requiring
the use of a meta-Terraform tool like terragrunt that would coordinate the
per-application root modules when connected root modules change.

However, having smaller root modules is good for Terraform performance (it's
already rather slow in `next/production`), and considering the potential volume
of Cloudflare Page, Cache, and WAF rules (we already have heaps, they're just
not in Terraform), I think this is a good opportunity to prevent unnecessarily
increasing the size of `next/production`.

```{admonition} Question to reviewers
Reviewers, I am curious what y'all think about renaming `org` to `github`. If we
want to keep that change super minimal, we can just rename the directory and
tfvars file. Nothing else technically needs to change, we don't even need to
move resources out of the `github` child module. This would serve to clarify the
boundary and purpose of that root module.
```

```{important}
Madison and Dhruv gave approval for this approach during review of the proposal.
We will use a new `cloudflare` root module and rename `org` to `github`. We will
remove the `github` child module from `org`/`github` root module: that's a "nice to
have" but is not strictly necessary, nor does it provide any significant benefit
making the work to move each resource into the root module out of a child module
worth it.
```

#### `register_with_target_group` removal

The `register_with_target_group` variable exists because `ec2-service` was
developed in conjunction with our Ansible playbooks, and as such, originally
leaned heavily into patterns that existed in our legacy EC2-based service
modules. In particular, it assumed that services would have their initial
configuration and start-up based in the `user_data` script (what we refer to as
`init.tpl`). This is no longer the pattern we will follow for EC2 instances, for
two reasons:

1. In order to move away from Terraform as a deployment tool so that we use it
   purely as a resource provisioning tool, we are slowly embracing Ansible as a
   tool for configuring and maintaining running services on EC2 instances. To
   keep this consistent, the Terraform modules should not contain explicit
   implementation details of the services (or at least avoid them as much as
   possible) so that we don't create multiple sources of truth. See
   [this comment in the legacy Elasticsearch `init.tpl` script for further exploration on this concept](https://github.com/WordPress/openverse-infrastructure/blob/9ec75430741aeb1bfb770e2f237e308c2a819716/modules/services/elasticsearch/init.tpl#L3-L47).
1. EC2 instances can be responsible for more than one service running on them.
   For example, there's no reason the EC2 instance running Kibana could not also
   run another non-critical internal service. Even with a small instance, there
   is plenty CPU and RAM to spare on it that would be best shared with another
   similar low-intensity service rather than paying for an additional EC2
   instance.

Both of these create a situation where the moment an EC2 instance is provisioned
and turns on for the first time (and runs the `user_data` script), there will
not be a service running on it. However, when registering a target to a target
group, the target _must_ respond on the port registered to the target group.
That is impossible if the service isn't running, e.g., after we've provisioned
the EC2 instance but before we've run the Ansible playbook to configure and
start the service for the first time.

Therefore, with this approach in mind, there are zero use cases for
`register_with_target_group`. It will _always_ be false when following our new
approach to EC2-based services, because we will always configure new services
using Ansible rather than the `user_data` script.

This change is not strictly necessary for this project, but given that we will
expand the usage of `ec2-service`, it's a good idea to do it now.

Despite the complex rationale, this step is relatively simple and will only
require deleting the `register_with_target_group` variable from
`generic/ec2-service` and removing its usage from the module. It _might_ require
`terraform state mv` because it will result in the removal of some `count`
declarations on resources in `generic/ec2-service`, but Terraform is recently
sometimes able to detect these moves without manual intervention.

#### Extract networking and domain configuration from `generic/service` and `generic/ec2-service` modules (`service-domain` and `service-networking`)

Both `generic/service` and `generic/ec2-service` include the following groups of
resources that share similar configurations between the modules:

- Security group
- Cloudflare domain management

For each of these, a foundational set of assumptions exist that are duplicated
either between `generic/service` and `generic/ec2-service` or between those
modules and `generic/service-alias`. In particular, canary configuration for
load balancer listeners related to domains and security group rules (including
the fundamental assumptions we have about how our services can be accessed) are
duplicated.

The two steps in the step-by-step plan will deduplicate these details and
consolidate the following information into purpose-fit modules that can be used
interchangeably with ECS and EC2 based services:

- That HTTP access to live services always through our load balancers, and as
  such should only need access on HTTP ports from origins within our VPC (in
  other words, no external HTTP access directly to public IPs or DNS endpoints).
- That SSH access to EC2 instances always runs through the SSH bastion (as of
  <https://github.com/WordPress/openverse-infrastructure/pull/743>) and as such
  port 22 only needs to accept connections from the SSH bastion and no where
  else.
- That services may have multiple names/aliases (for example, `api.` and
  `api-production.`) and those aliases must operate identically _without
  redirects_ (to prevent SEO issues), including when considering services with
  multiple, unbalanced targets (e.g., canary services with only 1 instances vs
  main services with >1 instance). In these cases, listeners must correctly
  weight targets in forwarding rules, and this is true of all aliases for the
  service. This in particular deduplicates subdomain handling in
  `generic/service` and `generic/service-alias`.

It's important to do these now, because after we add Airflow to the `next` root
modules and move the API to `openverse.org`, we'll have a whole host of new
subdomains and listeners to handle in distinct ways. We should do this now,
before that's the case, to avoid further complexity and juggling needed if we do
it afterwards.

Once this is finished, the API service configuration would look something like
this:

```
locals {
  nginx_port = 8080
}

module "security-group" {
  public_ports = [local.nginx_port]
  # ...
}

module "service" {
  security_group = module.security_group.sg
  public_port = local.nginx_port
  # ...
}

module "api-openverse-org" {
  source = "generic/service-domain"
  target_groups = module.service.targets
  name = "api"
  value = module.service.dns_name
  cf_zone = openverse_org_cf_zone
}

module "api-production-openverse-org" {
  source = "generic/service-domain"
  target_groups = module.service.targets
  name = "api-production"
  value = module.service.dns_name
  cf_zone = openverse_org_cf_zone
}
```

```{note}
Do not take the above as a concrete implementation example, I've just imagined
what it _could_ look like for the purposes of helping visualise how the new
generic networking modules would fit into existing services.
```

As with the other preliminary steps, this is not strictly necessary, but it's a
good opportunity to make this improvement and deduplicate these concerns out of
the various modules into shared locations. This will result in overall simpler
modules with more code reuse. It will, however, require juggling resources
around with `terraform state mv`, so it should not be considered trivial. For
live services, we will need to take care during implementation to prevent
downtime (though there isn't anything here that should strictly result in
downtime).

These should be implemented in two separate PRs, one for `service-domain` and
another for `security-group`.

##### `generic/service-domain`

The steps to implement this change are:

1. Rename `generic/service-alias` into `generic/service-domain` by duplicating
   the existing module into the updated name, then convert all instances of
   `generic/service-alias` to `generic/service-domain`. This may require
   `tf state mv`. Finally, delete `generic/service-alias`.
1. Update `generic/service-domain` to accept a list of target group
   configuration objects rather than a `service` module instance. This makes the
   API more flexible and less tied to `generic/service`'s implementation
   details.

   - The variable to replace `service` should be named something like
     `target_groups` and have the following signature:

   ```
   variable "target_groups" {
     type = list(object({
       // `aws_target_group` object
       target_group = any
       // The weight of this target relative to others in the list. This could be, for example, the number of ECS tasks running in the service registered to the target group or the number of EC2 instances registered to the target group
       // If there is a single target, this is ignored
       weight = optional(number, null)
     }))

     validation {
       condition = len(var.target_groups) == 1 || alltrue([for tg in var.target_groups: tg.weight != null])
       error_message = "Target group configurations must include weight when multiple target groups exist"
     }
   }
   ```

   - Rather than `service.has_canary`, the new module should use
     `len(var.target_groups) > 0` to determine whether to use weighted
     listeners.

1. Create new instances of `generic/service-domain` for the domains currently
   managed by existing `generic/service` and `generic/ec2-service` instances.
   These are the domains passed as `subdomain` to those modules, like
   `api-production` is passed to `service.production-api`. This will also
   require using `tf state mv` to reuse the existing resources in the generic
   service modules. Use a temporary variable `configure_domains` passed to the
   generic service modules to make it possible to do this service-by-service and
   in staging before production.
1. After all services have all domains configured using `generic/service-domain`
   and `configure_domains = false` on their generic service module instances,
   remove domain configuration from the generic services and the temporary
   `configure_domains` variable.

Implement all of this first in staging, and then repeat the process in
production to avoid dangling changes in a production caused by `tf state mv` not
being reflected on `main`.

##### `generic/security-group`

This should be a good deal simpler than `generic/service-domain`.

1. Create the new `generic/security-group` module and have it configure a
   security group with the following, using `aws_security_group_rule` to ensure
   it's always possible to add rules to the security group outside the module:
   - Allow all outbound traffic. All our services currently do this, and it will
     be easy to make this conditional in the future if we need it, but we can
     avoid adding complexity here for now.
   - Accept traffic on ports configured as `public_ports`. We actually do not
     need ingress from Cloudflare directly to the service because all services
     have HTTP mediated through the load balancer, so access to the "public
     port" is always from within the VPC.
   - Allow SSH ingress from the SSH bastion only if `var.ssh = true`. This
     should be a variable because ECS services don't need it, but we want to use
     the same heuristic for all SSH access to EC2 instances.
   - These are the basic assumptions for all our services. If a service needs
     additional rules, rather than adding conditionals, the service should
     create purpose-fit `aws_security_group_rule` instances and attach them to
     the exported security group.
1. Add a temporary variable to generic service modules `create_security_group`
   that defaults to `true`. We'll use this to enable us in the next step to move
   security groups for each service one-by-one.
1. For each concrete service, first in staging then production, create an
   instance of `generic/security-group`, using `count` on the module to target
   staging first. Use `tf state mv` to move security groups out of the generic
   service module used for the concrete service and into the new
   `generic/security-group` instance.
   - For example, to do this for the frontend:
     - Create `generic/security-group` in `concrete/frontend` with
       `count = var.environment == "staging" ? 1 : 0`
     - Use `terraform state mv` to move
       `module.staging-frontend.module.service.aws_security_group.service` to
       `module.staging-frontend.module.security-group.aws_security_group.this`
     - Set `create_security_group` on the `generic/service` instance to
       `var.environment != "staging"`.

Repeat this until all generic service modules have
`create_security_group = false` and a dedicated `generic/security-group`
instance.

### Moving Airflow to `next`

[The steps listed above for Airflow](#1-move-airflow-to-airflowopenverseorg)
should be fairly straightforward, primarily, as I've said elsewhere, because
Airflow is not a zero-downtime service, so we don't need to worry about keeping
the same running instance the entire time.

Before we have the new Airflow instance up and running using the method in the
next section, we'll want to preemptively set up Cloudflare Access for the new
`airflow.openverse.org` domain. Do this by adding `airflow.openverse.org` to the
Cloudflare Access configuration
[in the new `cloudflare` root module](#moving-cloudflare-access-and-the-new-cloudflare-root-module).

When doing this, we should also add all Cloudflare Page, Cache, and WAF rules
related to Airflow over from `openverse.engineering` into the `cloudflare` root
module onto the `openverse.org` zone. Right now these are not configured in
Terraform, so we will take the opportunity now to do so.

To clarify the redirect expectations, we will _not_ redirect
`airflow.openverse.engineering` to `airflow.openverse.org`. This is an internal
service and there is no reason to maintain additional code to redirect it.

#### Deploy and maintain Airflow using Ansible

The complexity of this change will primarily come from adding significant new
functionality to our Ansible playbooks, in particular, the ability to read/write
secrets to environment variables on EC2 instances. Our Airflow instance has
[a _lot_ of environment variables configured in `init.tpl`](https://github.com/WordPress/openverse-infrastructure/blob/b9b5094124a6e96458544b722262c33bacf04b42/modules/services/catalog-airflow/init.tpl#L39-L77)
and all of these will need to be able to be managed by the Ansible playbook to
configure the service.

To do this, we will use Ansible Vault, with git-crypt used to lock the vault
password file.
[Refer to Ansible Vault's documentation here](https://docs.ansible.com/ansible/latest/vault_guide/index.html).
[This blog post from a Red Hat sysadmin does a good job describing how Ansible Vault works](https://www.redhat.com/sysadmin/ansible-playbooks-secrets).
We will use Ansible Vault to store the secrets themselves, and git-crypt to
encrypt/decrypt the password file used to unlock the vault. We won't use
git-crypt to encrypt/decrypt the secrets themselves because Ansible Vault has
excellent integration with Ansible playbooks, whereas if we used git-crypt we'd
need to invent a new way of managing hostvars or playbook template files.

Use `ansible.builtin.lineinfile` to sync secret environment variables into a
`sensitive.env` file. Environment variables that are not secret should just go
into the hostvars and templated into the compose file, rather than in the vault.
That will allow us to use `no_log: true` on `ansible.builtin.lineinfile` for
secrets that are in the vault, while still getting to see verbose diffs when
non-sensitive variables are changing.

Likewise, we'll take this opportunity to further reduce `init.tpl` for the new
Airflow EC2 instance to only configure the authorized keys and basic environment
variables. In reference to `generic/ec2-user-data`, this would mean setting
`install_docker` and `install_cloudwatch` to false. Instead, the new playbook to
manage our Airflow configuration will handle installing these dependencies as
well as configuring the CloudWatch agent. Use `ansible.builtin.yum` to manage
the dependencies (make sure to pin their versions!) and `ansible.builtin.script`
to install the docker compose plugin when needed (make sure to use compose v2
for this, rather than the v1 used by `catalog-airflow/init.tpl`). Our Airflow
configuration also requires `git`, used by the DAG sync script, so install that
too. In the future we'll augment the playbook to include the option to update
these dependencies.

Re-write the compose file as `compose.yml.jinja2` in `ansible/airflow/templates`
to follow the compose v2 convention and explicit Jinja2 template naming. Refer
to `ansible/kibana/templates/compose.yml.jinja2` for an example of this.
Remember to use the `sensitive.env` file for secrets so that we can safely diff
the compose file without logging secrets, separate from changes to the sensitive
environment variables.

Store the `openverse-catalog` tag in the Airflow hostvars to make it easy to
update during deployments. Update the `just bump` recipe to modify the hostvars
file instead of the Terraform file.

In the playbook, include a step to check if the data refresh or other critical
DAGs are running, and disallow deployment if they are (include a `force`
variable to override this functionality). Use the Airflow CLI to determine DAG
state.

### Moving the API

In contrast to the Airflow work, the API does not need a full new deployment for
this, primarily because it is already in the `next` root modules. Instead, the
work for the API is concerned only with adding the new `openverse.org` domains
to point to the existing API service, and then turning the
`openverse.engineering` ones into redirects. There is also support work involved
to notify registered applications of the change, including a management command
to email them and a Make post to draft and publish.

Potentially the most complex aspect of this is actually the Cloudflare redirect
rule to send API traffic from the `openverse.engineering` domains to
`openverse.org`. I am 95% confident that we can do this with a single dynamic
redirect rule, which is available in the free tier.

The rule should match requests using something like the following expression:

```
http.host matches "api(-production)?\.openverse.engineering"
```

As mentioned in the step-by-step section, we will only redirect production
domains. This reduces the complexity of the match expression and the dynamic
target expression below. It also helps to clarify the fact that staging is
volatile and has no guarantees for anyone using it (which is mostly us).

The expression should also temporarily look for a special header's presence,
acting as a feature flag, so that we don't immediately start to redirect normal
users and can test the redirect:

```
any(http.request.headers.names[*] == "x-openverse-redirect") and http.host matches "api(-production)?\.openverse.engineering"
```

Then, because we are only redirecting production, the match expression is
thankfully trivial and does not require `regex_replace` or other string
manipulation:

```
concat("https://api.openverse.org", http.request.uri)
```

We cannot modify query parameters in the redirect, so there's nothing we can do
to re-write the `url` parameter to the oembed endpoint. Luckily, that endpoint's
request serializer ignores the hostname of the `url` parameter altogether, so it
won't cause a backwards compatibility issue.

As mentioned in the step-by-step section, we will configure this rule in
[the `cloudflare` root module](#moving-cloudflare-access-and-the-new-cloudflare-root-module).

### Finalizing the move

The finalization steps handle cleaning up documentation and other non-critical
references, as well as announcing the change on Make. Old links to production
API will continue to work as redirects, so there's no need to update them right
away.

## Dependencies

### Feature flags

<!-- List feature flags/environment variables that will be utilised in the development of this plan. -->

We will utilise the following temporary Terraform variables for certain stages
of the work (all covered in detail above):

- `configure_domains`
- `create_security_group`

These will be removed by the time their relevant steps are complete.

### Infrastructure

<!-- Describe any infrastructure that will need to be provisioned or modified. In particular, identify associated potential cost changes. -->

This entire project is fundamentally an infrastructure one, with small changes
to the API and frontend code to support it.

As covered above, the effect of this is a savings of 250 USD per month, once we
can downgrade the `openverse.engineering` Cloudflare account to the free tier.

### Other projects or work

<!-- Note any projects this plan is dependent on. -->

This project blocks our effort to reintroduce comprehensive rate limiting to our
frontend and API. The details of that work are covered in
[this issue in the private Openverse infrastructure repository](https://github.com/WordPress/openverse-infrastructure/issues/747).

## Rollback

<!-- How do we roll back this solution in the event of failure? Are there any steps that can not easily be rolled back? -->

The only critical rollback to keep in mind is when we turn off the special
header that controls the new Cloudflare redirect rule.

When we remove the header condition, we should be ready to immediately add it
back, in case we see signs that the redirect is not working the way it is
intended to.

At this point we will already have tested the fact that `api.openverse.org` is
correctly accepting requests and forming responses using the correct domain, so
the only potential issue would be if the redirect causes a controllable issue
for a large number of users, or if we missed a critical edge case.

In those cases, we can just add the header condition back or manually turn the
redirect rule off in the Cloudflare dashboard, whichever is easiest at the time.

## Privacy

<!-- How does this approach protect users' privacy? -->

There are no privacy considerations for this project. Nothing is changing with
how we store or present data.

## Localization

<!-- Any translation or regional requirements? Any differing legal requirements based on user location? -->

Only the email and Make post call for new copy, and we localise neither.
Therefore, this project requires no localisation.

## Risks

<!-- What risks are we taking with this solution? Are there risks that once taken can’t be undone?-->

There is inherent and unavoidable risk that a large number of integrations do
not follow redirects, and would start failing. There's nothing we can do about
this, unless we wish to maintain direct access to the API from
`openverse.engineering`. However, that would preclude us from gaining the
benefits of this work, and if that ends up being the case, this truly would have
been for naught, because it makes the blocked rate limiting approach impossible
and prevents us from downgrading the Cloudflare zone to the free tier.

## Prior art

<!-- Include links to documents and resources that you used when coming up with your solution. Credit people who have contributed to the solution that you wish to acknowledge. -->

[The project thread issue contains some valuable preliminary discussion and links to related work Dhruv and Zack did when we first started thinking about this move](https://github.com/WordPress/openverse/issues/2038).
