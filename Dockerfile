FROM node:14-alpine

# directory for the app in the container
WORKDIR /usr/app

# copies all the app's files from host into the container folder which
# might include the node_modules dir if npm install executed in the host
COPY . /usr/app

# removes any existing node_modules folder
# this prevents the host's node_modules from being used in the container
# which could cause issues with native binaries such as node_sass.
RUN rm -rf /usr/app/node_modules/

ENV CYPRESS_INSTALL_BINARY=0

RUN npm install -g npm@7.21.0 && \
    npm install && \
    npm run i18n:get-translations
