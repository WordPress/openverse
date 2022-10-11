FROM node:16-alpine as builder

# Install system packages needed to build on macOS
RUN apk add --no-cache --virtual .gyp python3 make g++ \
  && npm install -g pnpm

USER node

WORKDIR /home/node/app

COPY --chown=node:node pnpm-lock.yaml .

# install dependencies including local development tools
RUN pnpm fetch

# copy the rest of the content
COPY --chown=node:node . /home/node/app

# Prevent pre-commit from being installed, we don't need it here and it fails to install anyway
ENV SKIP_PRE_COMMIT=true

RUN pnpm install -r --offline

# disable telemetry when building the app
ENV NUXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

ARG API_URL
ARG RELEASE

RUN echo "{\"release\":\"${RELEASE}\"}" > /home/node/app/src/static/version.json

RUN pnpm i18n
RUN pnpm build:only

###################
#    Nuxt app
###################

FROM node:16-alpine as app

# Install CURL for the production healthcheck
RUN apk --no-cache add curl

WORKDIR /home/node/app

USER node

COPY --from=builder --chown=node:node /home/node/app .

# set app serving to permissive / assigned
ENV NUXT_HOST=0.0.0.0

# set application port
ENV PORT=8443

# expose port 8443 by default
EXPOSE 8443

ENTRYPOINT [ "npm", "start", "--" ]
