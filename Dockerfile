# ==
# builder
# ==

# application builder
FROM node:16 AS builder

WORKDIR /usr/app

# copy package.json and package-lock.json files
COPY package*.json .

# install dependencies including local development tools
RUN npm install

# copy the rest of the content
COPY . /usr/app

# disable telemetry when building the app
ENV NUXT_TELEMETRY_DISABLED=1

# build the application and generate a distribution package
RUN npm run build

# ==
# development
# ==
# application for development purposes
FROM node:16 AS dev

WORKDIR /usr/app

ENV NODE_ENV=development
ENV CYPRESS_INSTALL_BINARY=0

# copy files from local machine
COPY . /usr/app

# disable telemetry when building the app
ENV NUXT_TELEMETRY_DISABLED=1

# install dependencies (development dependencies included)
RUN npm install

# expose port 8443
EXPOSE 8443

# run the application in development mode
ENTRYPOINT [ "npm", "run", "dev" ]

# ==
# production
# ==
# application package (for production)
FROM node:alpine AS app

WORKDIR /usr/app

ENV NODE_ENV=production
ENV PLAYWRIGHT_SKIP_BROWSER_GC=1

# copy the package.json and package-lock.json files
COPY package*.json .

# copy the nuxt configuration file
COPY --from=builder /usr/app/nuxt.config.js .

# copy distribution directory with the static content
COPY --from=builder /usr/app/.nuxt /usr/app/.nuxt

# copy some files required by nuxt.config.js
COPY --from=builder /usr/app/src/locales /usr/app/src/locales
COPY --from=builder /usr/app/src/utils  /usr/app/src/utils

RUN npm ci --only=production --ignore-script

# set app serving to permissive / assigned
ENV NUXT_HOST=0.0.0.0

# set app port
ENV NUXT_PORT=8443

# set application port
ENV PORT=8443

# expose port 8443 by default
EXPOSE 8443

# run the application in static mode
ENTRYPOINT ["npm", "start"]

