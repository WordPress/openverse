FROM node:8.12.0-alpine

# installs npm modules for the container in a temp directory
WORKDIR /tmp
COPY package.json /tmp/
RUN npm install

# directory for the app in the container
WORKDIR /usr/app

# copies all the app's files from host into the container folder which 
# might include the node_modules dir if npm install executed in the host
COPY . /usr/app

RUN rm -rf /usr/app/node_modules

# movies container's node_modules into the apps directory
# this prevents the host's node_modules from being used in the container
# which could cause issues with native binaries such as node_sass.
RUN mv /tmp/node_modules /usr/app/
