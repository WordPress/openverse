refer_sample = """
You can refer to the cURL request samples for examples on how to consume this
endpoint.
"""


def fields_to_md(field_names):
    """
    Create a Markdown representation of the given list of names to use in
    Swagger documentation.

    :param field_names: the list of field names to convert to Markdown
    :return: the names as a Markdown string
    """

    *all_but_last, last = field_names
    all_but_last = ", ".join([f"`{name}`" for name in all_but_last])
    return f"{all_but_last} and `{last}`"


class MediaSearch:
    desc = f"""
Results are ranked in order of relevance and paginated on the basis of the `page` param.
The `page_size` param controls the total number of pages.

Although there may be millions of relevant records, only the most relevant several
thousand records can be viewed. This is by design: the search endpoint should be used to
find the top 10,000 most relevant results, not for exhaustive search or bulk download of
every barely relevant result. As such, the caller should not try to access pages beyond
`page_count`, or else the server will reject the query.

For more precise results, you can go to the
[Openverse Syntax Guide](https://search.creativecommons.org/search-help)
for information about creating queries and
[Apache Lucene Syntax Guide](https://lucene.apache.org/core/2_9_4/queryparsersyntax.html)
for information on structuring advanced searches.

{refer_sample}"""  # noqa: E501


class MediaStats:
    desc = f"""
You can use this endpoint to get details about content providers such as `source_name`,
`display_name`, and `source_url` along with a count of the number of individual items
indexed from them.

{refer_sample}"""


class MediaDetail:
    desc = refer_sample


class MediaRelated:
    desc = refer_sample


class MediaComplain:
    desc = f"""
By using this endpoint, you can report a file if it infringes copyright, contains mature
or sensitive content and others.

{refer_sample}"""
