const github = require('@actions/github')
const core = require('@actions/core')

const githubMeta = {
  projectBoardID: 70,
  projectStatusColumnName: 'Status',
  repoOwner: 'wordpress',
  repo: 'openverse',
}

const allowedStatuses = ['In Kickoff', 'In RFC', 'In Progress', 'Shipped']

const GET_PROJECT_CARDS = `
  query {
    repository(name:"${githubMeta.repo}", owner:"${githubMeta.repoOwner}") {
      projectV2(number: ${githubMeta.projectBoardID}) {
        items(last: 100) {
          nodes {
            id
            fieldValueByName(name: "${githubMeta.projectStatusColumnName}") {
              ...on ProjectV2ItemFieldSingleSelectValue {
                name
              }
            }
            content {
              __typename
              ...on Issue {
                id
                url
                assignees(first:10) {
                  nodes {
                    login
                  }
                }
                author {
                  login
                }
                comments(last:100) {
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

async function run() {
  try {
    const octokit = github.getOctokit(process.env.ACCESS_TOKEN)
    const isDryRun = process.env.DRY_RUN === 'true' ?? true

    // Fetch project cards with their associated issue data
    const result = await octokit.graphql(GET_PROJECT_CARDS)

    const currentDate = new Date()

    for (const node of result.repository.projectV2.items.nodes) {
      const issue = node.content
      if (issue.__typename !== 'Issue') continue

      // Check the status of the card
      const status = node.fieldValueByName.name
      if (allowedStatuses.includes(status)) continue

      const comments = issue.comments.nodes
      const fourteenDaysAgo = new Date(
        currentDate.setDate(currentDate.getDate() - 14)
      )

      if (
        // Check if the issue has been commented on in the last 14 days
        !comments.some(
          (comment) => new Date(comment.createdAt) > fourteenDaysAgo
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
          const [, , , owner, repo, , issue_number] = issue.url.split('/')

          await octokit.rest.issues.createComment({
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

run()
