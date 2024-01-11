import { defineEventHandler } from "h3"

import { LOCAL, PRODUCTION } from "~/constants/deploy-env"

/**
 * Send the correct robots.txt information per-environment.
 */
export default defineEventHandler(() => {
  const deployEnv = process.env.DEPLOYMENT_ENV ?? LOCAL

  const contents =
    deployEnv === PRODUCTION
      ? `# Block search result pages
User-agent: *
Disallow: /search/audio/
Disallow: /search/image/
Disallow: /search/
Disallow: /image/
Disallow: /audio/
      `
      : `# Block crawlers from the staging site
User-agent: *
Disallow: /
`

  return contents.replaceAll("\n", "<br />")
})
