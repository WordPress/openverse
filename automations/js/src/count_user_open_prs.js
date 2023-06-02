// @ts-check

/**
 * Checks the open PR count for the current Github actor.
 * Return their Slack username and PR count, if found.
 *
 * @param {Object} options
 * @param {import('@octokit/rest').Octokit} options.github
 * @param {import('@actions/github')['context']} options.context
 * @param {import('@actions/core')} options.core
 */
module.exports = async ({ github, context, core }) => {
  const { GITHUB_REPOSITORY, GH_SLACK_USERNAME_MAP } = process.env

  if (!GITHUB_REPOSITORY || !GH_SLACK_USERNAME_MAP) {
    core.setFailed('Required dependencies were not supplied')
  }

  const [owner, repo] = GITHUB_REPOSITORY.split('/')
  const slackUsername = JSON.parse(GH_SLACK_USERNAME_MAP)[context.actor]

  const GET_PULL_REQUESTS = `
      query ($author: String!, $repoOwner: String!, $repo: String!) {
        repository(name:$repo, owner:$repoOwner) {
          pullRequests(states:OPEN, first:100, author:$author) {
            nodes {
              isDraft
            }
          }
        }
      }
    `

  try {
    const result = await github.graphql(GET_PULL_REQUESTS, {
      author: context.actor,
      repoOwner: owner,
      repo: repo,
    })

    const reviewablePRs = result.repository.pullRequests.nodes.filter(
      (pr) => !pr.isDraft
    )

    if (slackUsername) {
      return {
        pr_count: reviewablePRs.length,
        slack_username: slackUsername,
      }
    } else {
      core.warning(`Slack username not found for ${context.actor}.`)
      return {}
    }
  } catch (error) {
    core.setFailed(`Error fetching pull requests: ${error.message}`)
  }
}
