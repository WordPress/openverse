# ==
# builder
# ==

# application builder
FROM node:16 AS builder

WORKDIR /usr/app

ARG API_URL

# Install pnpm
RUN npm install -g pnpm

# copy package.json and package-lock.json files
COPY package.json .
COPY pnpm-lock.yaml .
COPY .npmrc .

# install dependencies including local development tools
RUN pnpm install --store=pnpm-store

# copy the rest of the content
COPY . /usr/app

# disable telemetry when building the app
ENV NUXT_TELEMETRY_DISABLED=1

# build the application and generate a distribution package
RUN pnpm build

# ==
# development
# ==
# application for development purposes
FROM node:16 AS dev

WORKDIR /usr/app

# Install pnpm
RUN npm install -g pnpm

ENV NODE_ENV=development
ENV CYPRESS_INSTALL_BINARY=0

# copy files from local machine
COPY . /usr/app

COPY --from=builder /usr/app/pnpm-store /usr/app/pnpm-store

# disable telemetry when building the app
ENV NUXT_TELEMETRY_DISABLED=1

# install dependencies (development dependencies included)
RUN pnpm install --store=pnpm-store

# expose port 8443
EXPOSE 8443

# run the application in development mode
ENTRYPOINT [ "pnpm", "run", "dev" ]

# ==
# production
# ==
# application package (for production)
FROM node:16-alpine AS app

WORKDIR /usr/app

# Install pnpm
RUN npm install -g pnpm

ENV NODE_ENV=production
ENV PLAYWRIGHT_SKIP_BROWSER_GC=1

# copy package.json and package-lock.json files
COPY package.json .
COPY pnpm-lock.yaml .
COPY .npmrc .

# copy the nuxt configuration file
COPY --from=builder /usr/app/nuxt.config.ts .

# copy distribution directory with the static content
COPY --from=builder /usr/app/.nuxt /usr/app/.nuxt

# copy publically-accessible static assets
COPY --from=builder /usr/app/src/static /usr/app/src/static

# Copy over files needed by Nuxt's runtime process
COPY --from=builder /usr/app/src/locales /usr/app/src/locales
COPY --from=builder /usr/app/src/utils  /usr/app/src/utils
COPY --from=builder /usr/app/src/constants  /usr/app/src/constants
COPY --from=builder /usr/app/src/server-middleware  /usr/app/src/server-middleware
COPY --from=builder /usr/app/pnpm-store /usr/app/pnpm-store

RUN pnpm install --frozen-lockfile --store=pnpm-store

# set app serving to permissive / assigned
ENV NUXT_HOST=0.0.0.0

# set app port
ENV NUXT_PORT=8443

# set application port
ENV PORT=8443

# expose port 8443 by default
EXPOSE 8443

# run the application in static mode
ENTRYPOINT ["pnpm", "run", "start"]
