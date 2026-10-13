# 2023-03-09 Project Proposal: Detecting sensitive textual content and blurring all sensitive results

**Author**: @sarayourfriend

## Reviewers

- [x] @aetherunbound
- [x] @krysal

## Project summary

Detect results with sensitive textual content by checking their textual content
against a list of sensitive terms. Once results with sensitive terms in their
textual content are determined, blur those results on the frontend.

> **Note** We acknowledge that we are making an inference about results based on
> textual context. That inference applies specifically to the textual content
> _only_, but is also likely to apply to content itself (whether image or
> audio). We also acknowledge the various pit-falls that can come with this
> approach as well as its insufficiency. However, it's the best approach we can
> implement now, in a timely manner, that will substantively improve the
> accessibility of Openverse.

## Goals

This advances Openverse's goal of increasing the safety of the platform.

## Requirements

> **A note on tone**: This section should be mostly readable and understandable
> by casual, non-technical readers. However, certain aspects of it unavoidably
> delve into technical details in order to describe how features fit together or
> considerations that will need to be kept in mind during implementation
> planning. These need to be documented _somewhere_, and displacing them from
> the requirements felt strange. If you are not interested in these particular
> technical details, please skip the two sections titled "Implementation
> details" and the section on "How to blur results". These sections in
> particular consider technical issues of the project that may confound readers
> unfamiliar with software development whether applied to Openverse or more
> generally.

### API

#### Filtering

The Django API is able to filter out results that include sensitive terms in
their textual content. It does so without degrading search performance.

Results with sensitive terms in their textual content are only included in
results when `include_sensitive_results=True`. This parameter will supplant the
`mature=True` as a more comprehensively and descriptively named parameter.
`mature=True` should still work, but it should just be an alias for
`include_sensitive_results` and should be marked as deprecated in or altogether
excluded from the API documentation.

##### Implementation details

This will likely be implemented as a secondary index of results that do not
include the sensitive terms, as explored in
https://github.com/WordPress/openverse-api/pull/1108.

#### Designation of results with sensitive terms

Results that include sensitive terms in their textual content are so denoted in
the API results in a new result field named `sensitivity`. Sensitivity should be
an array that should be empty for results where `mature = false` and the textual
content does not contain any sensitive terms. For results marked as `mature`,
the array should include a `"mature"` string. For results with sensitive terms
in their textual content, the array should include a `"sensitive_text"` string.
At this time we will not be denoting _what_ sensitive terms are present nor will
we be developing any categories of terms. This approach leaves open the
potential for that in the future, however, by allowing the array to include
specific tokens for particular categories of sensitivity, whether derived from a
categorisation of the sensitive terms list, or from an image classification API.

Note that this designation needs to happen both in the search endpoint and in
the single result endpoint. Each endpoint may need a different approach to
achieve this. In particular, the approach taken will depend on whether
Elasticsearch or Python is used to mark results as sensitive.

##### Implementation details

There are two broad approaches that can be taken for this. I am actively
consulting with people more familiar with Elasticsearch for the best way to do
this, but the broad strokes of this are that we will either:

- Loop over results in Python and use a Regex to determine if textual content on
  the result includes sensitive terms. The results of this will be cached in
  Redis to ameliorate performance degradation over time.
- Use a script field and multi-index search to determine in Elasticsearch and as
  a hit property whether the result is included in the filtered index (and is
  therefore "safe").

There may also be other viable ways of performing this determination in
Elasticsearch, but the detail remains. If the determination is made in Python,
then it is easy to share the implementation between the search endpoint and the
single result endpoint (and both can benefit from the Redis caching). If the
determination is made in Elasticsearch and benefits from Elasticsearch's full
text search, then we may need to change the single result endpoint to pull the
result in question from Elasticsearch rather than Postgres, leveraging the
`_source` property on hits. This could be a big, complex change, though and
might require big infrastructural overhauls and challenge assumptions built into
the Django app. The alternative is that we maintain two approaches to doing so:
the cached Python method for single results and Elasticsearch approach for
search with the goal of unifying the approaches in the future.

### Frontend

Sensitive results never appear for users who have not opted-in to including
sensitive results in their query. This feature will be built off the existing
"mature" filter but enhanced with better UI and more comprehensive/less
suggestive language. The API query parameter is not present in the frontend
search route's query parameters. Instead, the setting is set within a session
cookie and the filter applied at query time (rather than being passed through
via the query params of the page). **Note that this differs from the
implementation of the "mature" filter that previously existed**. This is
discussed in further depth in the [settings persistence](#settings-persistence)
and [outstanding questions](#outstanding-questions) sections below.

Sensitive results on the search results page are blurred. Users can unblur and
reblur individual results through a simple and clear interaction on the search
results page. In addition to being able to opt-in to having sensitive results
included in their query, users can disable blurring by default. This parameter
is stored in the application state. If users disable blurring by default, there
is not an option to "reblur" images.

Results unblurred by the user on the search results page are also unblurred if
they visit the single result page for that result. Results that have not been
unblurred remain blurred upon navigating to the single results page.

If a user lands directly on a single result page for a result with sensitive
textual content, the result is always blurred by default. This is true
regardless of whether the user has disabled blurring by default on the search
results page, but only applies to page navigation _directly_ to a single results
page rather than a client side navigation.

#### Settings persistence

Right now, the recommendation is to store the "include sensitive results"
setting in session cookie and the "do not blur sensitive results" setting in the
ephemeral application state. "Include sensitive settings" should not be reset by
a page reload, but "do not blur sensitive results" should. To summarise:

| Setting                       | Default | Persistence location            | Behaviour implications                                                                                                                                              |
| ----------------------------- | ------- | ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Include sensitive results     | Off     | Session cookie                  | Cannot be manipulated through the query params. Does not reset on page reload or in new tabs. Does reset when the browser is restarted or when the session expires. |
| Do not blur sensitive results | Off     | Application state (Pinia store) | Cannot be manipulated through the query params. Resets on page reloads and in new tabs and is independent of the browser session.                                   |

Compared to Google and DuckDuckGo image searches' behaviour, ours would be more
or less equivalent (with additional safety from blurring). Neither Google nor
DDG, as far as I can tell, store the safe search setting in the query
parameters. Instead, they store it as a session variable. Neither have an option
to blur sensitive results, so there is no comparison to be made along those
lines.

The only variation to this approach I considered was to persist the "include
sensitive results" setting in the query parameters like we did for the "mature"
filter that used to exist. The risk of this without blurring is obvious: a
malicious user can create a query with the setting enabled, hide it behind a URL
shortener, and trick a victim into seeing a query with results they did not
consent to. The risk of this is mitigated by blurring sensitive results by
default, but landing on a page full of blurred results might set a curious young
person up for seeing something they didn't anticipate or want to see, simply
because they didn't realise _why_ the image was blurred. This could be further
mitigated by very clear messaging, but that could potentially clutter the search
results UI and persisting the setting in the query params does not give any
clear benefit that I can think of.

## Outstanding questions

### "Include sensitive results" persistence

As described in the [settings persistence](#settings-persistence) section above,
one outstanding question is how to store the "include sensitive results" option.
The current recommendation is to use a session cookie. Discussed above is
storing the setting in the query params (with reasons why we shouldn't do this).
The only other option is to store the setting in the ephemeral application state
the way we will store the "do not blur sensitive results" option.

To simply phrase the question to reviewers: **What is your preference for
storing the "include sensitive results" option and why?**.

Above I've recommended the session cookie approach because I think it strikes a
reasonable balance between usability and safety. If someone really wants to
include sensitive results, they won't be annoyed by having to re-enable the
setting every time they reload the page or open a new tab within the same
session. However, it will also reset so that shared computers will not subject
subsequent users to the sensitive preferences of previous ones.

I am totally open to not seeking that balance and going fully into safety mode
and only persisting the setting in ephemeral application state, requiring it to
be re-enabled any time the page is reloaded or for new tabs. If other folks
think this is a preferable option, I am happy to change the feature descriptions
above to reflect that.

I am almost entirely closed to the option of storing the option in the query
params. It gives no discernible benefit in my estimation but comes with risks
that are counter-productive to the goals of this project. If there is a strong
argument to be made it favour if this approach, however, please share it.

### How to blur results

There are three known viable approaches to blurring results. One is
significantly simpler than the other two. If you know of others, please raise
them in review.

1. Blur using a CSS filter.
2. Blur using [BlurHash](https://github.com/woltapp/blurhash).
3. Blur using
   [Low Quality Image Placeholders (LQIP)](https://github.com/transitive-bullshit/lqip-modern).

> **Note**: Photon, the image proxy we use, does
> [have an option to apply two different types of blurs to images](https://developer.wordpress.com/docs/photon/api/#filter).
> This could be used to obviate the issue with blurring client-side on low-spec
> devices. However, we cannot control the degree of blurring and the current
> behaviour does not blur the image sufficiently to obscure its contents. This
> could lead to thinking that we could blur in our own thumbnail endpoint, but
> that would be more resource intensive than using BlurHash (I believe). While
> BlurHash is technically complex to implement, I do think it is the best
> approach for reasons I will describe below. LQIP could also be resource
> intensive for the API, but ameliorated with caching.

#### CSS filter

This is the simplest option and only requires adding a `filter: blur(Xrem)`
style to sensitive results.

This option has the following downsides:

- It is a basic Gaussian blur and may not sufficiently obscure the image if a
  low number is used or may create an unsettling blob effect if a higher number
  is used
- Gaussian blur may not be as aesthetically pleasing as the alternative
- It requires the image to be downloaded to be blurred by the client

Initially I speculated that client-side Gaussian blurring may have adverse
effects on low-spec hardware's accessibility of the site. However, I've tested
this locally by modifying the frontend to blur all images and visiting the local
site on my PinePhone, on a low-spec quad-core ARM laptop, and on a US$30 Android
phone. On none of these devices could I perceive a degradation in performance.
Keep in mind these are all devices that are already very slow! They were able to
render a full page of image results blurred at 1rem, without issue.

It has one significant upside in that it is supremely simple to implement, does
not require any new dependencies, and would only require about few lines of
frontend code rather than lots of frontend and API code to support it.
Additionally, the image would quickly load after being unblurred by the user
because it would just require removing the CSS style rather than getting the
actual image.

#### BlurHash

This is a significantly more complex option that requires both API and frontend
changes to support. Rather than sending the image to the client, the thumbnail
URL would send a hashed version of the image that represents the blur. A client
side library decodes the hash and displays it in place of the thumbnail. It
would require two new dependencies, a JavaScript BlurHash decoder to render the
hash in a canvas and an API library to produce the hash from the thumbnail.

It has the following downsides:

- Significantly more complicated than Gaussian blur
- Requires conditionally calculating the hash on the API side in the thumbnail
  endpoint
  - This would be done by using a new query parameter on the thumbnail endpoint
    to request the blurred hash
- Can have a performance impact on the thumbnail endpoint
- Introduces a delay between when the image is unblurred when it is displayed
  due to needing to download the actual thumbnail
- Could have different performance issues if decoding the hash is a heavy
  operation for low-spec clients
  - Looking at the code, I highly doubt this because it's a
    [fast bit of maths](https://github.com/mad-gooze/fast-blurhash/blob/main/index.js)
    that (due to the nature of BlurHash) ignores almost all the content of the
    image rather than a Gaussian blur which needs to consider ever aspect of the
    image in order to apply the blur
- It may have its own client-side performance issues due to clients needing to
  render canvas for each image in view

It has the following upsides:

- Does not require the client to download the image just to blur it
  - If the client never unblurs an image, it will have saved all the bytes of
    the image from being downloaded to the client
- We can easily cache the hash in Redis to ameliorate performance over time
  - If we do so, then we could use the hash for other things down the line (like
    average colour filters) and add it directly to the documents via the same
    ETL pipeline we'll develop for dead links, further ameliorating any API
    performance issues
- Does not rely on the client's ability to apply and render a Gaussian blur
  transformation to potentially several images on a single page
- Extremely minor and only barely relevant: If we calculated the BlurHash for
  all images in the future in our re-crawler, we could use them as placeholders
  rather than the skeleton boxes we currently use

#### LQIP (modern)

This approach generates a very low quality version of the image and passes that
to the frontend for scaling to the placeholder size and then blurring.
[There is an example implementation in JavaScript](https://github.com/transitive-bullshit/lqip-modern).

It has all the same downsides as BlurHash (aside from hash decoding) in addition
to the fact that we would need to reimplement it in Python. As far as I can
tell, there is no Python implementation ready for us to use. Performance issues
on the API side can be amortised through caching. It does not have the same
potential client-side performance issue as BlurHash as it only requires scaling
and blurring an image. We know low-spec hardware can handle blurring, and
scaling is a trivial operation for most hardware.

It has similar upsides to BlurHash. Critically, compared to BlurHash it:

- Does not require the client to render the hash in a canvas
- Uses image scaling and blurring on an image with very small amounts of
  information, meaning the client-side Gaussian blur will be less heavy than
  blurring the full thumbnail

However, unlike BlurHash, it has almost no practical future usage for us with
respect to image analysis.

#### Recommendation

We should implement the CSS blurring solution first. It is an iterative
improvement on the current solution and is the fastest way to bring the
improvements to users.

Therefore, provided we cannot identify real device accessibility concerns
(noting my experiments [covered above](#css-filter)), we should proceed with the
client-side CSS blurring, with a follow-up proposal requested to evaluate
switching to BlurHash, LQIP, or some other more advanced solution from which we
might receive additional benefits. This proposal request is not urgent and
should be triaged in the context of our other scheduled projects.

If we had infinite time, I think BlurHash would be the best choice—provided it
itself does not end up having device accessibility issues—for the following
reasons:

1. While significantly more complex, it is not sufficiently complex to be
   burdensome. The simplicity of the CSS filter makes BlurHash look monstrous,
   but in the grand scheme of things, it's actually a relatively simple approach
   to blurring the images.
2. It avoids performance issues with relying on low-spec clients to apply
   Gaussian blurs to potentially several images.
3. BlurHash hashes have significant future value and all potential API level
   performance issues can be ameliorated through caching hashes with Redis.

The only significant downside that I think exists is the delay between
unblurring and displaying the full image due to needing to download the full
unblurred image. However, I think this is balanced out by the bytes saved over
the network in _not_ sending images that might potentially never be unblurred.

More important, however, is getting the benefits of this broad feature out to
users as soon as we can without compromising on the initial quality. We can do
so using client-side CSS blurring.

For reviewers: **What are you feelings on this issue and why?**. Do you think it
is worth investing time up front in BlurHash, LQIP, or another solution; or is
it fine to push that off to a later date as a potential future improvement to
the feature?

## Measurements and success criteria

The project will be a success once we are able to safely and accessibly serve
sensitive results to users. This is qualified by the fact that this is an
initial solution and not the totality of what we wish to do in order to make
Openverse safer and more broadly accessible.

The success of that project rests on the completion of its technical
implementation. However, we can add the following events to the API and frontend
to better understand the usage of the features.

### API

- `SENSITIVE_RESULT_COUNT`
  - Sent for each query where the search param `include_sensitive_results` is
    set to `True`. It should include a raw count of the number of results with
    sensitive textual content or with `mature` set to `True`. Not sent for
    results where the search params would not include sensitive results.
  - Allows us to measure the saturation of sensitive results for queries that
    include them.

### Frontend

Each of these are intended for measuring the usage of the feature to which they
relate.

- `TOGGLE_SENSITIVE_RESULTS`
  - Sent each time the "include sensitive results" setting is toggled.
  - Include a prop noting if the setting was being toggled on or off.
- `UNBLUR_SENSITIVE_RESULT`
  - Sent each time a result is unblurred. This should include a property
    denoting whether it on the single result or search results page.
  - Include media ID (in case this proves useful).
- `REBLUR_SENSITIVE_RESULT`
  - Sent each time a result is reblurred. This should include a property
    denoting whether it on the single result or search results page.
  - Include media ID (in case this proves useful).
- `TOGGLE_DO_NOT_BLUR`
  - Sent each time the "do not blur sensitive results" setting is toggled.
  - Include a prop noting if the setting was being toggled on or off.

## Participants and stakeholders

- Lead: @sarayourfriend
- Design: @panchovm
- Implementation:
  - @sarayourfriend
  - TBD
- Stakeholders:
  - Team lead: @zackkrida
  - Design: @panchovm & @WordPress/gutenberg-design

## Infrastructure

There are no infrastructure changes anticipated for this project.

## Accessibility

The various blurring approaches have potential device accessibility questions
that need to be answered. For now, sticking with client-side CSS filtering, we
should not have an issue with device accessibility.

UI accessibility remains a priority. The frontend implementation plan should
include clear instructions for ensuring the designs are implemented in an
accessible way.

## Marketing

We can coordinate with marketing to describe the new feature and its motivations
and celebrate the increased safety for users, especially young people, using
Openverse. In particular, we may be able to collaborate with educators that use
Openverse and share what improving the accessibility of Openverse in this way
means to them and their students.

## Required implementation plans

In the order they should be completed:

1. API filtering and designation implementation plan.

   - Must cover efficiently filtering out results with sensitive textual content
     in addition to including the `sensitivity` designation on each result.
   - Note the implementation detail considerations in the
     [filtering](#implementation-details) and
     [designation](#implementation-details-1) sections above.

2. Frontend implementation plan for settings management and blurring/unblurring
   images

   - Must cover the UI changes requested by design, management of both new
     settings, and displaying the blurred image with the ability to unblur.
   - Must cover accessibility testing for the new UI elements, especially the
     unblur/reblur controls.

## Dependent implementation plans

The actual implementation of the two implementation plans requested in this
proposal are blocked by the implementation of the
[sensitive terms list, as proposed here](https://github.com/WordPress/openverse/pull/911).
