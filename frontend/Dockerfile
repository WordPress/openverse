# syntax=docker/dockerfile:1
# check=skip=InvalidDefaultArgInFrom

# Automatically build image using Node.js version specified in `package.json`.
ARG FRONTEND_NODE_VERSION

###################
# Node.js builder #
###################

FROM docker.io/node:${FRONTEND_NODE_VERSION}-alpine AS builder

ARG SEMANTIC_VERSION

# Install system packages needed to build on macOS
RUN apk add --no-cache --virtual .gyp python3 make g++ \
  && npm install -g corepack@0.31.0 && corepack enable pnpm

USER node

WORKDIR /home/node/

# Copy monorepo mocking files into `/home/node`, which pretends to be the monorepo root.
# Note: these files must be manually un-ignored in the root .dockerignore
# hadolint ignore=DL3022
COPY --from=repo_root --chown=node:node .npmrc .pnpmfile.cjs pnpm-lock.yaml ./
RUN echo '{"packages":["frontend/"]}' > pnpm-workspace.yaml

# Copy the `frontend/` directory into `/home/node/frontend`, as a package in the monorepo.
COPY --chown=node:node . ./frontend/

WORKDIR /home/node/frontend

# Prevent pre-commit from being installed, we don't need it here and it fails to install anyway
ENV SKIP_PRE_COMMIT=true

# Get rid of the lockfile as it won't be accurate for the build without workspace.
# Then install dependencies, and in the process:
#   - fix the missing lockfile by writing a new one
RUN pnpm install

# disable telemetry when building the app
ENV NUXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

# Increase memory limit for the build process (necessary for i18n routes)
ENV NODE_OPTIONS="--max_old_space_size=4096"
ENV SEMANTIC_VERSION=${SEMANTIC_VERSION}

# Use the Sentry auth token secret to send the sourcemaps to Sentry only if the secret is provided
RUN --mount=type=secret,id=sentry_auth_token,mode=0444 \
    sh -c 'if [ -f /run/secrets/sentry_auth_token ]; then \
      SENTRY_AUTH_TOKEN="$(cat /run/secrets/sentry_auth_token)" && \
      echo "SENTRY_AUTH_TOKEN=$SENTRY_AUTH_TOKEN" >> .env.sentry-build-plugin && \
      echo "Using Sentry Auth Token: $SENTRY_AUTH_TOKEN"; \
    else \
      echo "No Sentry Auth Token provided"; \
    fi' && pnpm build


############
# Nuxt app #
############

FROM docker.io/node:${FRONTEND_NODE_VERSION}-alpine AS app

LABEL org.opencontainers.image.source="https://github.com/WordPress/openverse"

# Install CURL for the production healthcheck
RUN apk --no-cache add curl

WORKDIR /home/node/

USER node

COPY --from=builder --chown=node:node /home/node/node_modules ./node_modules/
COPY --from=builder --chown=node:node /home/node/frontend ./frontend/

WORKDIR /home/node/frontend/

ARG SEMANTIC_VERSION

# set app serving to permissive / assigned
ENV NUXT_HOST=0.0.0.0

# set application port
ENV PORT=8443

# expose port 8443 by default
EXPOSE 8443

ENTRYPOINT [ "npm", "start", "--" ]
