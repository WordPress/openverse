FROM node:16-alpine

RUN npm install -g pnpm pm2@5.2.0

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

COPY ecosystem.config.js /home/node/app/ecosystem.config.js

# set app serving to permissive / assigned
ENV NUXT_HOST=0.0.0.0

# set application port
ENV PORT=8443

# expose port 8443 by default
EXPOSE 8443

CMD ["pm2-runtime", "start", "ecosystem.config.js"]
