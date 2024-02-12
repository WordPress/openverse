# Stack

This page is your gateway to understanding our diverse technology stack. Explore code repositories on GitHub, access detailed documentation, and learn about the tools, frameworks, and languages driving each stack of the Openverse platform.

1. Catalog
   - Powered by Apache Airflow, it stores Openverse metadata efficiently.
   - [Code](https://github.com/WordPress/openverse/blob/main/catalog)
   - [Documentation](https://docs.openverse.org/catalog/index.html)
   - Language: Python
   - Tools and Framework:
     - [Apache Airflow](https://airflow.apache.org/docs/apache-airflow-providers-google/stable/operators/cloud/datacatalog.html)
2. Ingestion Server
   - The mechanism for refreshing the data from the catalog to the API.
   - [Code](https://github.com/WordPress/openverse/blob/main/ingestion_server)
   - [Documentation](https://docs.openverse.org/ingestion_server/index.html)
   - Language: Python
   - Tools and Framework:
     - [Elasticsearch](https://www.elastic.co/guide/index.html)
     - [Docker](https://docs.docker.com/)
3. API
   - Built with Django REST, it enables database querying for the Frontend.
   - [Code](https://github.com/WordPress/openverse/blob/main/api)
   - [Documentation](https://docs.openverse.org/api/index.html)
   - Language: Python
   - Tools and Framework:
     - [Django REST Framework](https://www.django-rest-framework.org/)
     - [Docker](https://docs.docker.com/)
4. Frontend
   - The public search engine at [openverse.org](https://openverse.org/), built with Vue and Nuxt.
   - [Code](https://github.com/WordPress/openverse/blob/main/frontend)
   - [Documentation](https://docs.openverse.org/frontend/index.html)
   - Language: JavaScript, HTML, CSS
   - Tools and Framework:
     - [Nuxt.js](https://nuxt.com/docs/getting-started/introduction)
     - [Vue.js](https://vuejs.org/guide/introduction.html)
     - [Node.js](https://nodejs.org/docs/latest/api/)
     - [Tailwind CSS](https://v2.tailwindcss.com/docs)
5. Automation
   - Scripts used for various workflows around Openverse repositories and processes.
   - [Code](https://github.com/WordPress/openverse/tree/main/automations)
   - [Documentation](https://docs.openverse.org/automations/index.html)
   - Language: Python
   - Tools and Framework:
     - [Node.js](https://nodejs.org/docs/latest/api/)
     

 



