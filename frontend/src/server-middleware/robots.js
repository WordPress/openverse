const { LOCAL, PRODUCTION } = require("../constants/deploy-env")

const AI_ROBOTS_CONTENT = `
# Block known AI crawlers
User-agent: GPTBot
Disallow: /

User-agent: CCBot
Disallow: /

User-agent: ChatGPT-User
Disallow: /

User-agent: Google-Extended
Disallow: /

User-agent: anthropic-ai
Disallow: /

User-agent: Omgilibot
Disallow: /

User-agent: Omgili
Disallow: /

User-agent: FacebookBot
Disallow: /

User-agent: Diffbot
Disallow: /

User-agent: Bytespider
Disallow: /

User-agent: ImagesiftBot
Disallow: /

User-agent: cohere-ai
Disallow: /

`

/**
 * Send the correct robots.txt information per-environment.
 */
export default function robots(_, res) {
  const deployEnv = process.env.DEPLOYMENT_ENV ?? LOCAL

  const contents =
    deployEnv === PRODUCTION
      ? `# Block search result pages
User-agent: *
Crawl-delay: 10
Disallow: /search/audio/
Disallow: /search/image/
Disallow: /search/
Disallow: /image/
Disallow: /audio/

crawl-delay:
${AI_ROBOTS_CONTENT}
      `
      : `# Block everyone from the staging site
User-agent: *
Disallow: /
`

  res.setHeader("Content-Type", "text/plain")
  res.end(contents)
}
