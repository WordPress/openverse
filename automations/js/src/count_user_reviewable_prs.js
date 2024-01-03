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
  const slackID = JSON.parse(GH_SLACK_USERNAME_MAP)[context.actor]

  if (!GITHUB_REPOSITORY || !GH_SLACK_USERNAME_MAP) {
    core.setFailed('Required dependencies were not supplied')
  }

  if (!slackID) {
    core.warning(`Slack username not found for ${context.actor}.`)
    return {}
  }

  const GET_PULL_REQUESTS = `
query ($repoOwner: String!, $repo: String!, $cursor: String) {
  repository(name:$repo, owner:$repoOwner) {
    pullRequests(states:OPEN, first:100, after: $cursor) {
      pageInfo {
        endCursor
      }
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
        createdAt
      }
    }
  }
}
`
  const ignoredLabels = [
    '🤖 aspect: text',
    '🧱 stack: documentation',
    '🟥 priority: critical',
  ]
  const [owner, repo] = GITHUB_REPOSITORY.split('/')
  const isValidPR = (pr) =>
    pr.author.login === context.actor &&
    !pr.isDraft &&
    !pr.labels.nodes.some((label) => ignoredLabels.includes(label.name))

  try {
    let hasNextPage = true
    let cursor = null
    let reviewablePRs = []
    while (hasNextPage) {
      const result = await github.graphql(GET_PULL_REQUESTS, {
        repoOwner: owner,
        repo: repo,
        cursor: cursor,
      })

      const { nodes, pageInfo } = result.repository.pullRequests
      const validPRs = nodes.filter(isValidPR)
      reviewablePRs.push(...validPRs)

      if (pageInfo.hasNextPage) {
        cursor = pageInfo.endCursor
      } else {
        hasNextPage = false
      }
    }

    let shouldAlert = false
    if (reviewablePRs.length >= 1) {
      // Get the most recently created PR, then determine if it's valid
      shouldAlert = isValidPR(
        reviewablePRs.sort((a, b) => a.createdAt.localeCompare(b.createdAt))[0]
      )
    }

    const result = {
      pr_count: reviewablePRs.length,
      slack_id: slackID,
      should_alert: shouldAlert,
    }
    core.info(`Current user has ${result.pr_count} PR(s).`)
    core.info(
      `Most recent PR should trigger alert based on labels: ${result.should_alert}`
    )
    core.setOutput('pr_count', result.pr_count)
    core.setOutput('slack_id', result.slack_id)
    core.setOutput('should_alert', result.should_alert)
  } catch (error) {
    core.setFailed(`Error fetching pull requests: ${error.message}`)
  }
}
