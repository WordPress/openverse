FROM node:8.12.0-alpine

# directory for the app in the container
WORKDIR /usr/app

# copies all the app's files from host into the container folder which 
# might include the node_modules dir if npm install executed in the host
COPY . /usr/app

# removes any existing node_modules folder
# this prevents the host's node_modules from being used in the container
# which could cause issues with native binaries such as node_sass.
RUN rm -rf /usr/app/node_modules/

RUN npm install