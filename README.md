# cccatalog-frontend

## About

Repository containing the [CC Search](https://ccsearch.creativecommons.org/) frontend application. This web app contains all the UI which communicates with the [CC Search API](https://github.com/creativecommons/cccatalog-api) to get the data that is rendered in the browser.

CC Search is an interface to search for content that is licensed under Creative Commons licenses or in the public domain.



The frontend app is built using [Vue.JS](https://vuejs.org/), [Babel](https://babeljs.io/) and [Webpack](https://webpack.js.org/).

## Getting Started

Run the following commands in order to have the code up and running on your machine:

``` bash
# installs dependencies
$ npm install

# Builds and serves assets with hot-reload 
$ npm run dev
```

### Docker setup

Alternatively, you can use Docker to build and run the application. You just have to run:

``` bash
$ docker-compose up
```

You should now have the application running and accessible at https://localhost:8443 (note: it runs on https://, not http://). Since it runs on HTTPS, you will probably see a invalid certificate privacy notice on your browser when accessing it. Just follow your browser's instructions to continue and access the website anyway.

## Running tests

You can run the tests by executing:
``` bash
npm run test
```

## Deployment

Details about how to deploy the frontend code can be found on the [CC Wiki](https://wikijs.creativecommons.org/tech/cc-search/frontend) (Accessible to CC Staff only).
