# Search Algorithm

Openverse currently uses a relatively simple and naïve search algorithm with
restricted modifications to the default Elasticsearch behaviour. The
documentation on this page was written by referencing the code in Openverse as
well as parts of Openverse's historical development. Parts of the story for how
Openverse's indexes came to be configured as they are today are likely missing.
Future improvements to Openverse's indexing and search will be more carefully
documented here and in the code to ensure there is greater longevitiy of
understanding.

> **Note**: This document avoids covering details covered in the
> [Openverse Search Guide](https://wordpress.org/openverse/search-help).
> Specifically, this document does not describe _how_ to search (advanced
> techniques and syntax), rather _what is searched_ and in what way.

## Reference resources

This document includes links to specific parts of Elasticsearch's documentation
and Openverse code. The following are broadly useful entry points into learning
about Elasticsearch, full text-search, and Openverse's index configuration:

- [Elasticsearch 7.12 documentation](https://www.elastic.co/guide/en/elasticsearch/reference/7.12/index.html)
- [Full-text search (Wikipedia)](https://en.wikipedia.org/wiki/Full-text_search)
- [Stemming (Wikipedia)](https://en.wikipedia.org/wiki/Stemming)
- [`es_mapping.py` (index configuration)](https://github.com/WordPress/openverse-api/blob/main/ingestion_server/ingestion_server/es_mapping.py)

## Terms

- "Document": The total queryable information representing a single work
  catalogued in Openverse.
- "Field": The individual queryable elements of a document. In the context of
  Openverse, these may be textual, numerical, or keywords.
- "Keyword field": A field where the entire contents of the field are treated as
  a single token. This is used for fields where the possible values are a known
  and relatively small set. For example, descriptive
  ["size" of an image](https://github.com/WordPress/openverse-api/blob/d9f83e53761dd502c93384f0aa6e2f7b711151e2/api/catalog/api/constants/field_values.py#L22-L26)
  may be either "large", "medium", or "small". Because we know this ahead of
  time, Elasticsearch is able to much more quickly create the index entries for
  documents with this field because there are essentially only three keys that
  need to be indexed.
- "Result relevance": An individual result is "relevant" to a search when it
  matches the expectations of the user for a given query. A result is irrelevant
  if it does not match the expectations of the user for that same query. For
  example, the query "bird watch" may produce pictures of a wristwatch with a
  bird clock face illustration _or_ could surface pictures related to the
  activity also known as "birding" (bird watching), due to stemming. In the case
  of this specific query, "bird watching" may not be relevant, despite being a
  technically correct match for the query given Openverse's current index
  configuration. Other relevancy issues may be caused by descriptions that are
  not related to the contents of an image. This often happens on Flickr where
  users sometimes include blog-like text in the description of an image that
  references things that happened outside the context of the image itself.
- "Result quality": A combination of relevance and other factors like the actual
  perceived "quality" of a given work. A work may be directly relevant to a
  particular query but be of low quality. Quality is subjective, though there
  may be certain characteristics that are broadly applicable to some subset of
  searches.

## Technology

Openverse uses Elasticsearch's
[full text indexing and search capabilities](https://www.elastic.co/guide/en/elasticsearch/reference/7.12/full-text-queries.html).
We currently rely heavily on Elasticsearch's default behaviours in many aspects
of our search including Elasticsearch's default stemming configuration, aside
from small adjustments documented in the
[text analysis and stemming](#text-analysistokenization) section below. The
"raw" index configuration can be found in the `es_mapping.py` module (see link
in [resources](#reference-resources)). Information for how to understand the
configuration can be found in the
[Elasticsearch documentation for index configuration](https://www.elastic.co/guide/en/elasticsearch/reference/7.12/index-modules.html).

> **Note**: We also apply cluster-level configurations as part of our
> Elasticsearch deployment. These are intentionally not covered here as they
> primarily deal with cluster performance and are irrelevant to the way searches
> are executed.

## Text analysis/tokenization

> **Note**: A general understanding of
> [full-text search (Wikipedia)](https://en.wikipedia.org/wiki/Full-text_search)
> and the concepts of
> ["stemming" (Wikipedia)](https://en.wikipedia.org/wiki/Stemming) and
> ["tokenization" (Wikipedia)](https://en.wikipedia.org/wiki/Lexical_analysis#Tokenization)
> will be useful for understanding this section.

Text analysis or tokenization is the broad process Elasticsearch follows to
generate the indexable list of words for each document. A significant aspect of
this for Openverse (and many applications) is
[stemming](https://www.elastic.co/guide/en/elasticsearch/reference/7.12/stemming.html).
When Elasticsearch performs a full text search, it is searching the index which
maps stemmed words to a specific document, rather than the original text itself.
This means that the text analysis configuration applied has a significant impact
on the way documents are searched, how Elasticsearch calculates relevance, and,
in particular, what terms are available for a given document. When searching for
"animal", for example, if the document does not contain the word animal in any
of the indexed fields, then it will _never_ be returned as a result (under the
current configuration). Said another way: whether a document will be returned
for a given query depends exclusively on the tokens derived when textual
analysis is applied to the document.

Openverse only applies our custom text analysis configuration to the "title",
"description", and "tags" fields. All other fields use the
[standard analyzer](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/analysis-standard-analyzer.html).

Openverse is currently configured exclusively with English language text
analysis. This means Openverse does not properly index documents in any language
other than English. This is a known issue that we hope to be able to address
soon via Elasticsearch's internationalisation tools.

We primarily use the default English language stemming settings aside from
[minor changes (GitHub)](https://github.com/cc-archive/cccatalog-api/issues/574#issue-668091876)
present in the `es_mapping.py` configuration to address a specific issue with
the "anim" stem. We use the
[Snowball English stemmer](https://snowballstem.org/algorithms/porter/stemmer.html)
and
[Lucene's possessive English stemmer](https://lucene.apache.org/core/8_8_0/analyzers-common/org/apache/lucene/analysis/en/EnglishPossessiveFilter.html).

The rationale for this specific stemmer configuration is not documented aside
from the "anim" stem issue linked above.

Openverse also applies the `lowercase` text analysis filter making our indexes
case-insensitive.

## Search execution

There are essentially 2 broad types of "full-text" searches available via the
Openverse API:

1. General "query" searching, which applies a simple text query search against
   several, non-configurable fields.
2. Individual field querying, which enables searching specific fields with
   independent query terms.

Both of these search types also allow keyword filtering of the results by the
following fields:

- Extension
- Category
- Source
- License
- License type
- Length (audio only)
- Aspect ratio (image only)
- Size (image only)

Source is the only field for which you can currently also specify exclusions.

By default, items marked "mature" are excluded, but these can also be enabled.

See the following API documentation links for descriptions and options for each
field:

- [Audio search](https://api.openverse.engineering/v1/#operation/audio_search)
- [Image search](https://api.openverse.engineering/v1/#operation/image_search)

For each of these fields, there is a limited and specific set of terms that
appear for the relevant document fields for each of these query parameters.
These fields are matched exactly, using the filter context Elasticsearch queries
("filter" or "must_not"). Filter-context queries can be cached by Elasticsearch,
which improves their performance. All of these filters except for `extension`
are validated to only allow specific options (documented in the API
documentation links above).

### General "query" searching

This is the type of searching most commonly used to query Openverse. It is
activated when the `q` query parameter is present. It searches the following
aspects of a document:

- Description
- Title
- Tags

> **Note**: The API does not currently surface the "description" field, though
> [discussion is underway](https://github.com/WordPress/openverse-catalog/issues/364)
> to potentially change this fact.

Of these, title is weighted 10000 times more heavily than the description and
tags. This makes works whose titles closely match the query rise to the "top" of
the results, even if the same text is present word-for-word in a description. It
also breaks ties between documents, if, for example, two documents are returned,
one because the title matches and one because a tag matches, the title-matched
document will be ranked higher and therefore appear first.

Additionally, if the query is wrapped in double quotes (`"`), we search each of
these _exactly_ which will bypass stemming and match exact word order. Title
weighting is still applied in this case. This means that if the exact query text
is found in the title of one document and the description of another, the
title-matched document will appear ahead of the description-matched document.

### Individual field querying

This type of search is not commonly used. The Openverse frontend only surfaces
one of the subset of fields that are queryable in this approach. It is only
available if the `q` query parameter is excluded. In other words, if the request
includes the `q` query parameter, _the API will ignore these options even if
they are present in the request_. In that case, it will execute the
[general "query" search](#general-query-searching) described above. Future work
may surface the possibility for combining general querying and individual field
querying.

These are the fields currently supported for individual field querying:

- Creator
- Title
- Tags

> **Note**: The "tags" filter applies to the `name` field of the tags. No other
> aspect of the tags is currently searchable.

Each of these can be stacked. You can make a request that queries for a specific
title by a specific creator. The following parameters would search only for
works by "Claude Monet" where the word "madame" (or it's stemmed versions)
appear in the title: `?creator=Claude Monet&title=madame`.

As you can see, this is unique from the general query searching in that it
allows you to apply separate queries for individual fields (hence the name
"individual field querying"). The other notable difference from general querying
is that the "description" field of the document is not available for individual
field querying.

## Document scoring

Aside from the aforementioned weighting of document "title" matches, Openverse
also includes one other attempt at scoring documents to improve search relevancy
and quality. Future improvements to Openverse's search relevancy will most
likely involve changes to how we score documents. For example, we may score
documents higher if they are determined to be popular results in Openverse
itself.

### Provider supplied popularity

Some providers supply a "popularity" rating for individual works. We ingest this
data and calculate a normalised "popularity" score named `rank_feature`. Flickr
is one of the providers that supplies this information. This data is used so
that works that are popular on the provider side, are ranked higher in Openverse
as well. The assumption here is that works that are popular on the provider's
own website are likely higher quality and therefore more desirable results.
Whether this has a significant impact on result relevancy or quality has not
been measured, in part due to loose definitions of "relevancy" and "quality" and
in part because we do not currently have tools for measuring user perception of
a results relevancy or quality.
