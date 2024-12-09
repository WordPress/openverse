# Stack

This page is your gateway to understanding our diverse technology stack. Explore
code repositories on GitHub, access detailed documentation, and learn about the
tools, frameworks, and languages driving each stack of the Openverse platform.

1. Catalog
   - The Apache Airflow-powered system for downloading and storing Openverse's
     metadata
   - [Code](https://github.com/WordPress/openverse/blob/main/catalog)
   - [Documentation](https://docs.openverse.org/catalog/index.html)
   - Language: Python
   - Tools and Framework:
     - [Apache Airflow](https://airflow.apache.org/docs/apache-airflow/stable/index.html)
2. Ingestion Server
   - The mechanism for refreshing the data from the catalog to the API DB and
     Elasticsearch indices
   - [Code](https://github.com/WordPress/openverse/blob/main/ingestion_server)
   - [Documentation](https://docs.openverse.org/ingestion_server/index.html)
   - Language: Python
   - Tools and Framework:
     - [Elasticsearch](https://www.elastic.co/guide/index.html)
     - [PostgreSQL](https://www.postgresql.org/docs/)
3. API
   - The Django REST API for querying the database, used by the frontend
   - [Code](https://github.com/WordPress/openverse/blob/main/api)
   - [Documentation](https://docs.openverse.org/api/index.html)
   - Language: Python
   - Tools and Framework:
     - [Django](https://docs.djangoproject.com/en/5.0/)
     - [Django REST Framework](https://www.django-rest-framework.org/)
4. Frontend
   - The public search engine at [openverse.org](https://openverse.org/), built
     with Vue and Nuxt
   - [Code](https://github.com/WordPress/openverse/blob/main/frontend)
   - [Documentation](https://docs.openverse.org/frontend/index.html)
   - Language: TypeScript / Node.js
   - Tools and Framework:
     - [Nuxt.js](https://nuxt.com/docs/getting-started/introduction)
     - [Vue.js](https://vuejs.org/guide/introduction.html)
5. External Services
   - Cache: [Redis](https://redis.io/docs/about/)
   - Upstream and API database: [PostgreSQL](https://www.postgresql.org/docs/)
   - Analytics: third-party, [Plausible](https://plausible.io/docs)
   - Search: [Elasticsearch](https://www.elastic.co/guide/index.html)
