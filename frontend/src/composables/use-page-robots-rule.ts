import { useRobotsRule, useSiteConfig } from "#imports"

/**
 * Robots meta tag and header instructions for pages
 * These are distinct from robots.txt rules because do not
 * want to prevent bots from viewing the pages altogether
 * in case they are visiting for e.g., embed information.
 * We _do_ want to disallow following links that will cause
 * rapid and unwanted crawling behaviour (e.g., related
 * results on a single result page, collection results, etc)
 *
 * Pages not listed here are either covered by the robots.txt
 * rules configured in nuxt.config.ts or are allowed to be
 * crawled with default settings (index and follow links)
 */
const pageRobots = {
  "single-result": "noindex, nofollow",
  "tag-collection": "noindex, nofollow",
  "source-collection": "index, nofollow",
  "creator-collection": "noindex, nofollow",
} as const

export const usePageRobotsRule = (page: keyof typeof pageRobots) => {
  const siteConfig = useSiteConfig()
  if (!siteConfig.indexable) {
    useRobotsRule("noindex, nofollow")
  } else {
    useRobotsRule(pageRobots[page])
  }
}
