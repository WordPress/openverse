FROM node:16-alpine as builder

# Install system packages needed to build on macOS
RUN apk add --no-cache --virtual .gyp python3 make g++ \
  && npm install -g pnpm

USER node

WORKDIR /home/node/

# Copy monorepo mocking files into `/home/node`, which pretends to be the monorepo root.
COPY --chown=node:node .npmrc .pnpmfile.cjs pnpm-lock.yaml ./
RUN echo '{"packages":["frontend/"]}' > pnpm-workspaces.yaml

# Copy the `frontend/` directory into `/home/node/frontend`, as a package in the monorepo.
COPY --chown=node:node . ./frontend/
# Remove the files copied into `frontend/` by `.github/workflows/ci_cd.yml`.
RUN rm ./frontend/.npmrc ./frontend/.pnpmfile.cjs ./frontend/pnpm-lock.yaml

# Fetch dependencies, including local development tools, to the virtual store.
RUN pnpm fetch

WORKDIR /home/node/frontend

# Prevent pre-commit from being installed, we don't need it here and it fails to install anyway
ENV SKIP_PRE_COMMIT=true

# Get rid of the lockfile as it won't be accurate for the build without workspace.
# Then install dependencies, and in the process:
#   - use only dependencies present in the virtual-store
#   - fix the missing lockfile by writing a new one
RUN pnpm install --offline

# disable telemetry when building the app
ENV NUXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

ARG API_URL
ARG RELEASE

RUN echo "{\"release\":\"${RELEASE}\"}" > /home/node/frontend/src/static/version.json

RUN pnpm build:only

###################
#    Nuxt app
###################

FROM node:16-alpine as app

LABEL org.opencontainers.image.source="https://github.com/WordPress/openverse"

# Install CURL for the production healthcheck
RUN apk --no-cache add curl

WORKDIR /home/node/

USER node

COPY --from=builder --chown=node:node /home/node/node_modules ./node_modules/
COPY --from=builder --chown=node:node /home/node/frontend ./frontend/

WORKDIR /home/node/frontend/

# set app serving to permissive / assigned
ENV NUXT_HOST=0.0.0.0

# set application port
ENV PORT=8443

# expose port 8443 by default
EXPOSE 8443

ENTRYPOINT [ "npm", "start", "--" ]
