const { LOCAL, PRODUCTION } = require("../constants/deploy-env")

const deniedUserAgents = [
  "GPTBot",
  "CCBot",
  "ChatGPT-User",
  "Google-Extended",
  "anthropic-ai",
  "Omgilibot",
  "Omgili",
  "FacebookBot",
  "Diffbot",
  "Bytespider",
  "ImagesiftBot",
  "cohere-ai",
  "ia_archiver", // Internet Archive for the Wayback Machine. Not malicious, but we don't want to allow single and search results to be indexed at the risk of preserving deindexed works.
]

const aiDisallowRules = deniedUserAgents
  .map((ua) => `User-agent: ${ua}\nDisallow: /\n`)
  .join("\n")

/**
 * Send the correct robots.txt information per-environment.
 */
export default function robots(_, res) {
  const deployEnv = process.env.DEPLOYMENT_ENV ?? LOCAL

  const contents =
    deployEnv === PRODUCTION
      ? `# Block search result pages and single result pages
User-agent: *
Crawl-delay: 10
Disallow: /search/audio/
Disallow: /search/image/
Disallow: /search/
Disallow: /image/
Disallow: /audio/
# Disallow the same for all translated routes
Disallow: /*/search/audio/
Disallow: /*/search/image/
Disallow: /*/search/
Disallow: /*/image/
Disallow: /*/audio/

${aiDisallowRules}
      `
      : `# Block everyone from the staging site
User-agent: *
Disallow: /
`

  res.setHeader("Content-Type", "text/plain")
  res.end(contents)
}
