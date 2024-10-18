// @ts-check

// The number of days a project must be updated within
const DAYS_UPDATED_WITHIN = 14

const activeDevelopmentStatuses = [
  "🚀 In Kickoff",
  "💬 In RFC",
  "🚧 In Progress",
]

const GET_PROJECT_CARDS = `
  query($repo: String!, $repoOwner: String!, $projectBoardID: Int!, $projectStatusColumnName: String!) {
    repository(name: $repo, owner: $repoOwner) {
      projectV2(number: $projectBoardID) {
        items(last: 100) {
          nodes {
            id
            fieldValueByName(name: $projectStatusColumnName) {
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
              }
            }
            content {
              __typename
              ... on Issue {
                id
                createdAt
                url
                state
                assignees(first: 10) {
                  nodes {
                    login
                  }
                }
                author {
                  login
                }
                comments(last: 100) {
                  nodes {
                    createdAt
                  }
                }
              }
            }
          }
        }
      }
    }
  }
`

/**
 * Check our GitHub project board cards for attached "project thread" issues.
 * Check the issues to see if they've been commented on in the correct timeframe;
 * if not notify the project lead.
 *
 * @param {Object} options
 * @param {import('@octokit/rest').Octokit} options.github
 * @param {import('@actions/core')} options.core
 */
module.exports = async ({ github, core }) => {
  try {
    // eslint-disable-next-line no-constant-binary-expression
    const isDryRun = process.env.DRY_RUN === "true" ?? false

    const currentDate = new Date()
    // Create a date by subtracting DAYS_UPDATED_WITHIN days
    // (converted to milliseconds) from the current date in milliseconds.
    const requiredUpdatedByDate = new Date(
      currentDate.getTime() - DAYS_UPDATED_WITHIN * 24 * 60 * 60 * 1000
    )

    // Fetch project cards with their associated issue data
    const result = await github.graphql(GET_PROJECT_CARDS, {
      projectBoardID: 70,
      projectStatusColumnName: "Status",
      repoOwner: "wordpress",
      repo: "openverse",
    })

    for (const node of result.repository.projectV2.items.nodes) {
      const issue = node.content
      // If we're not looking at an open issue older than the required update date, move along
      if (
        issue.__typename !== "Issue" ||
        issue.state !== "OPEN" ||
        new Date(issue.createdAt) > requiredUpdatedByDate
      ) {
        continue
      }

      // Check the status of the card to make sure the project is in active development
      const status = node.fieldValueByName.name
      if (!activeDevelopmentStatuses.includes(status)) {
        continue
      }

      const comments = issue.comments.nodes

      if (
        // Check if the issue has been commented on in the last 14 days
        !comments.some(
          (comment) => new Date(comment.createdAt) > requiredUpdatedByDate
        )
      ) {
        // If not, leave a reminder comment on the issue
        const recipient = issue.assignees.nodes[0]
          ? issue.assignees.nodes[0].login
          : issue.author.login

        const body = `Hi @${recipient}, this project has not received an update comment in 14 days. Please leave an update comment as soon as you can. See the [documentation on project updates](https://docs.openverse.org/projects/planning.html#providing-project-updates) for more information.`

        if (isDryRun) {
          core.info(`Would have commented on issue ${issue.url}: ${body}`)
        } else {
          // Extract the owner, repo, and issue number from the issue URL
          const [, , , owner, repo, , issue_number] = issue.url.split("/")

          await github.rest.issues.createComment({
            owner,
            repo,
            issue_number,
            body,
          })
        }
      }
    }
  } catch (error) {
    core.setFailed(error.message)
  }
}
