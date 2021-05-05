<!-- TITLE: CC Catalog Community Involvement -->
<!-- SUBTITLE: Plan to increase contribution from the community to CC Catalog -->

# Goals

In order to increase the level of community involvement in the CC Catalog
code base, we have identified the following broad goals:

- Make it as easy as possible to begin contributing code.
  - Maintain a codebase with obvious entrypoints where developers can jump in
    and contribute with as little initial overhead as possible. Ideally, only
    knowledge of basic python should be necessary.
  - Maintain a clean, readable codebase.
  - Maintain a codebase that conforms to PEP8
- Be able to merge contributor pull requests safely, and put them into
  production quickly, allowing contributors to see the results of their efforts
  in the real world.
  - Increase the safety / testability of the CC Catalog code base
  - Automate more of deployment
- Increase the visibility of CC Catalog as an avenue to contribute to Creative
  Commons.
  - Publicly document the areas of the code that are most amenable to
    contribution.
  - Advertise the desire for more contribution in CC Catalog.

# Action Plan

## Entrypoint to contribution

We have decided that one of the best places to jump into contribution to the
CC Catalog is to create a new script that pulls data from some previously
unknown (to Creative Commons) API, or modify one that already exists, adding new
information. In this document, we will refer to such a script as a Provider API
Script. Enabling such contributions, and advertising our hope for contribution
in that area will be the focus of the remainder of this document.

### Technical changes making contribution easier

It seems like the number one way to make it less of a technical burden to
contribute or modify a new Provider API Script is to make a clearer distinction
between the code which is 'generic', i.e., used (in some form) by _all_ Provider
API Scripts, and that which is specific to the API of a particular provider.

Conceptually, the only thing the Provider API Script should need to know is
about the Provider API itself, i.e., the

- request format(s) necessary to get information
- any authentication information -- require this to be settable as an
  environment variable for now.
- mapping from responses to different pieces of required information

From the perspective of the Provider API Script, the 'pieces of required
information' are required arguments to a public function provided by the
generic section of the code base, which adds information specific to a single
image (perhaps something like `add_image_info`). Additionally, a Provider API
Script should implement a specific 'interface' (used non-technically here)
specified by Creative Commons that we can call from other parts of our
infrastructure, e.g., Airflow. Once it has gathered the required info for a
single image, the Provider API Script should simply call `add_image_info` from
the generic part of the code base with the required information as arguments. The
Provider API Script should call some `commit` method from the generic portion of
the code base before it exits, signaling that all is well, and the loaded images
should be retained on disk for further processing.

The Generic Section of the code base should provide a class (inspired by a
Repository model, but slightly different / simplified) with a public method that
takes the desired pieces of information as arguments. This method should be
well-documented (both in its docstring, and in the README somehow). In
particular, the required types, and which arguments are required should be
obvious. The following steps should be performed in the generic section of the
code base after this function is called:

1. Validate the input for types
1. Add required generic info based on input e.g.,
   - derive license from license URL
   - derive version from license
   - derive source from provider
   - fill in watermarked false by default
1. Add the `.tsv` row representing the image to some temporary `.tsv` file.

The Generic Section of the code base should provide a `config.py` to store
information such as provider name strings.

The Generic Section of the code base should provide a way to define an Airflow
DAG that knows how to call the main function of a properly-written Provider API
Script.

Following are a series of steps (to be made into Github issues) that should move
us in the direction outlined in this section.

1. Write a class that can be imported into a Provider API Script, and which
   provides the model and functionality above, i.e.,:
   - Expose a public `add_image_info` (or some other name) function that lets
     the script add an image to an instance of the class.
   - Handle the verification of the given image data.
   - Log 'generic' things such as how many images have been imported in the
     current run
   - Expose a `commit` (or some other name) function that performs any broader
     validation, and moves temporary `.tsv` files to a permanent location to be
     picked up by the `loaderWorkflow.py` DAG.
   - _All_ common logic involved with processing image data should live in, or
     be accessed through this class, and preferably through the `add_image_info`
     function.
   - It would be nice if this class (or one of its imports) handled formatting
     `meta_data` dictionaries, `tags` lists, and could derive `license_` /
     `license_version` fields from a `license_url`.
   - Some of the functionality of [`etlMods.py`][etl_mods] should be reused.
1. Write a module with other functionality that is generic:
   - Other functionality from [`etlMods.py`][etl_mods] should be preserved,
     e.g., `requestContent`.
1. Rewrite `wikimediaCommons.py` into `wikimedia_commons.py` to serve as an
   example of how to use this class (this script makes sense because it needs
   rewriting to work around a current bug anyway).
   - Ensure that _all_ generic functionality is extracted from
     `wikimedia_commons.py`, and lives in the 'generic' section of the codebase.

Once these steps are complete, we should have a working example of the desired
model for Provider API Scripts, and their interaction with the generic portion
of the code base.

We should, if we like what we see after these changes, continue by rewriting all
current Provider API Scripts in the new way. This will serve as a test of the
new paradigm, and provide more examples for potential contributors to look at
when designing and writing their own script.

[etl_mods]: https://github.com/wordpress/openverse-catalog/blob/master/src/cc_catalog_airflow/dags/provider_api_scripts/modules/etlMods.py

### Technical changes making deployment of new Provider API Scripts safe and easy

As stated above, it would be nice if when a contributor has submitted their pull
request, we have the technical capability to quickly and safely get their
changes into production (should we so desire).

For this to be feasible, we need a considerably more robust test suite than
currently exists. For example, there is currently a simple, probably correct
[Pull Request][pull_request] languishing in limbo because it is a modification
of a public function used and potentially overridden in a number of other places
in the code base, and there are no tests to help us know if the modification is
having some unintended breaking effect somewhere else. Any section of the code
that is intended to interface with contributor-provided scripts or other code,
_must_ be reasonably-well tested, so that we can merge and deploy with
confidence. The sections of the code most relevant to Provider API Scripts
should be tackled first in this matter.

1. We should write a comprehensive test suite for `etlMods.py`. This module is
   used by every Provider API Script, and much of the functionality is untested.
1. We should be fastidious in our own testing practices whenever rewriting any
   Provider API Script, as an example of what we expect for testing.
1. We should make sure that public methods intended to be used by the Provider
   API Scripts are robust, well-tested, and give meaningful errors when called
   incorrectly.

As for deployment itself, we need to have a deployment set up that lets us both

- put new code into production quickly and safely
- test it in a realistic environment where applicable
- roll back to a previous state if things go poorly.

For now, It should be possible to simply `git pull` from the running ec2, and
the necessary pieces to run the Airflow DAGs, and their dependencies should all
end up in the correct places. This implies:

1. Restructuring the repo, and potentially splitting it into two pieces, to
   match the directory structure needed in prod.
1. Split all dags into smaller pieces, so that they can be modified without
   affecting other workflows.

Eventually, it'd be nice to set up an automated deployment process that handles
testing, and deployment to AWS after a `git push` has occurred (or something
merged into the master branch).

- We definitely need to split the repo before we're ready for that stage.

[pull_request]: https://github.com/wordpress/openverse-catalog/pulls

## Documentation of where and how to contribute

Once we're prepared on the technical front, I want to put easy-to-follow
instructions for adding a Provider API Script in the repo (probably in the
`README.md`. I want to 'advertise' that avenue for easily contributing in a
number of places: Slack, IRC, at conferences, etc. Perhaps blog posts (I'm not
convinced that wouldn't be preaching to the choir, though). I think it would be
_massively_ helpful to have a pipeline of pre-vetted(ish) providers, with
tickets that we can have conversations with potential contributors about what
the API looks like, what the priority of that provider is, and so on. I think a
regular ping on, e.g., Slack with a specific task (A message like: We'd like
someone to prepare a Provider API Script for Provider X. Here are precise
instructions for what needs to be done. Here's who to ask for help. Here are
some examples of other Provider API Scripts) would work over time to encourage
contribution.
