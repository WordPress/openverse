const { LOCAL, PRODUCTION } = require("../constants/deploy-env")

/**
 * Send the correct robots.txt information per-environment.
 */
export default function robots(_, res) {
  const deployEnv = process.env.DEPLOYMENT_ENV ?? LOCAL

  const contents =
    deployEnv === PRODUCTION
      ? `# This file is intentionally left blank`
      : `# Block crawlers from the staging site
User-agent: *
Disallow: /
`

  res.setHeader("Content-Type", "text/plain")
  res.end(contents)
}
