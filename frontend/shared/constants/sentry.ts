// Sentry v11 collects user info, cookies and request bodies by default; keep the v10 defaults.
// @see https://github.com/getsentry/sentry-javascript/blob/develop/MIGRATION.md#if-you-want-to-keep-the-v10-default-behavior
const piiDeny = { deny: ["forwarded", "-ip", "remote-", "via", "-user"] }

export const sentryDataCollection = {
  userInfo: false,
  cookies: false,
  httpHeaders: { request: piiDeny, response: piiDeny },
  httpBodies: [],
  urlQueryParams: piiDeny,
  genAI: { inputs: false, outputs: false },
  databaseQueryData: false,
  queues: false,
  graphQL: { document: false, variables: false },
}
