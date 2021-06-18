search_description_boilerplate = """
Although there may be millions of relevant records, only the most 
relevant several thousand records can be viewed. This is by design: 
the search endpoint should be used to find the top 10,000 most relevant 
results, not for exhaustive search or bulk download of every barely 
relevant result. As such, the caller should not try to access pages 
beyond `page_count`, or else the server will reject the query.

For more precise results, you can go to the 
[CC Search Syntax Guide](https://search.creativecommons.org/search-help) 
for information about creating queries and 
[Apache Lucene Syntax Guide](https://lucene.apache.org/core/2_9_4/queryparsersyntax.html)
for information on structuring advanced searches.

You can refer to the cURL request samples for examples on how to consume this
endpoint.
"""