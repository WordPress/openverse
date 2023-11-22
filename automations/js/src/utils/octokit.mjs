import { Octokit } from 'octokit'

/** the personal access token for the GitHub API */
const pat = process.env.ACCESS_TOKEN
if (!pat) {
  console.error('GitHub personal access token "ACCESS_TOKEN" is required.')
  process.exit(1)
}

/**
 * Get an authenticated instance of `Octokit` to make GitHub API calls.
 *
 * @returns {import('octokit').Octokit} an authenticated instance of `Octokit`
 */
export function getOctokit() {
  return new Octokit({ auth: pat })
}
