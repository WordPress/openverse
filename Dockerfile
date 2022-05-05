FROM node:16-alpine

ARG PNPM_VERSION

RUN npm install -g pnpm@${PNPM_VERSION}

USER node

WORKDIR /home/node/app

COPY pnpm-lock.yaml .

# install dependencies including local development tools
RUN pnpm fetch

# copy the rest of the content
COPY --chmod=777 . /home/node/app

RUN pnpm install -r --offline

# disable telemetry when building the app
ENV NUXT_TELEMETRY_DISABLED=1

ENV NODE_ENV=production

ARG API_URL

RUN pnpm i18n
# build the application and generate a distribution package
RUN pnpm build:only

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
