const { LOCAL, PRODUCTION } = require("../constants/deploy-env")

/**
 * Send the correct robots.txt information per-environment.
 */
export default function robots(_, res) {
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

  res.setHeader("Content-Type", "text/plain")
  res.end(contents)
}
