const github = require('@actions/github')
const core = require('@actions/core')

async function run() {
  try {
    const octokit = github.getOctokit(process.env.GITHUB_TOKEN)
    const context = github.context
    const isDryRun = core.getBooleanInput('dry_run') ?? false

    // Fetch all issues with the label "🧭 project: thread" and not labeled with "blocked"
    const { data: issues } = await octokit.rest.issues.listForRepo({
      owner: context.repo.owner,
      repo: context.repo.repo,
      labels: '🧭 project: thread,-blocked',
      state: 'open',
    })

    const currentDate = new Date()

    for (const issue of issues) {
      const { data: comments } = await octokit.rest.issues.listComments({
        owner: context.repo.owner,
        repo: context.repo.repo,
        issue_number: issue.number,
      })

      const fourteenDaysAgo = new Date(
        currentDate.setDate(currentDate.getDate() - 14)
      )

      if (
        // Check if the issue has been commented on in the last 14 days
        !comments.some(
          (comment) => new Date(comment.created_at) > fourteenDaysAgo
        )
      ) {
        // If not, leave a comment on the issue
        const recipient = issue.assignee
          ? issue.assignee.login
          : issue.user.login
        const body = `Hi @${recipient}, this project has not received an update comment in 14 days. Please leave an update comment as soon as you can. See the [documentation on project updates](https://docs.openverse.org/projects/planning.html#providing-project-updates) for more information.`

        if (isDryRun) {
          console.info(
            `Would have commented on issue #${issue.number}: ${body}`
          )
        } else {
          await octokit.rest.issues.createComment({
            owner: context.repo.owner,
            repo: context.repo.repo,
            issue_number: issue.number,
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
