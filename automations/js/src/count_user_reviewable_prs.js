// @ts-check

/**
 * Checks the reviewable PR count for the current Github actor.
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

  // Return early if no Slack username
  if (!slackUsername) {
    core.warning(`Slack username not found for ${context.actor}.`)
    return {}
  }

  const GET_PULL_REQUESTS = `
    query ($repoOwner: String!, $repo: String!, $cursor: String) {
      repository(name:$repo, owner:$repoOwner) {
        pullRequests(states:OPEN, first:100, after: $cursor) {
          nodes {
            author {
              login
            }
            labels(first: 100) {
              nodes {
                name
              }
            }
            isDraft
          }
        }
      }
    }
  `

  try {
    let hasNextPage = true
    let cursor = null
    let reviewablePRs = []

    const ignoredLabels = [
      '🤖 aspect: text',
      '🧱 stack: documentation',
      'priority: critical',
    ]

    while (hasNextPage) {
      const result = await github.graphql(GET_PULL_REQUESTS, {
        repoOwner: owner,
        repo: repo,
        cursor: cursor,
      })

      const { nodes, pageInfo } = result.repository.pullRequests
      reviewablePRs.push(...nodes)

      if (pageInfo.hasNextPage) {
        cursor = pageInfo.endCursor
      } else {
        hasNextPage = false
      }
    }

    reviewablePRs = reviewablePRs.filter(
      (pr) =>
        pr.author.login === context.actor &&
        !pr.isDraft &&
        !pr.labels.nodes.some((label) => ignoredLabels.includes(label.name))
    )

    return {
      pr_count: reviewablePRs.length,
      slack_username: slackUsername,
    }
  } catch (error) {
    core.setFailed(`Error fetching pull requests: ${error.message}`)
  }
}
