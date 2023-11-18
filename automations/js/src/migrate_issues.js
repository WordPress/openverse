const fs = require('fs')

const { Octokit } = require('octokit')

// TODO: add auth token
const octokit = new Octokit({
  auth: '',
  userAgent: 'Search issues app v.1.0.0',
})

async function getTargetIssues(previousOwner, targetLabel, repos) {
  const parseComments = (comments) => {
    if (comments.length === 0) {
      return []
    }
    return comments.map((comment) => {
      // Add a `>` symbol at the beginning of a new line
      // in comments to make them look like a quote
      comment.body
        .replace(/(\\r\\n){1,3}/g, '$1> ')
        .replace(/(\r\n){1,3}/g, '$1> ')

      return `${
        comment.author_association === 'CONTRIBUTOR' ? 'Issue author ' : ''
      }*${comment.user.login}* commented on ${new Date(
        comment.created_at
      ).toDateString()}:\n\n>${comment.body}\n[source](${comment.html_url})\n`
    })
  }

  function parseIssues(issues) {
    return issues
      .filter((issue) =>
        issue.labels.map((label) => label.name).includes(targetLabel)
      )
      .map((issue) => {
        const labelNames = issue.labels.map((label) => label.name)
        const repoNameParts = issue.repository_url.split('/')
        const repoName = repoNameParts[repoNameParts.length - 1]
        return {
          issueNumber: issue.number,
          repo: repoName,
          title: `${issue.title} (original #${issue.number})`,
          migrationNotice: `This issue has been migrated from the [CC Search ${
            repoName.split('-')[1]
          } repository](${issue.html_url})\n`,
          author: `Author: ${issue.user.login}\n`,
          date: `Date: ${new Date(issue.created_at).toDateString()}\n`,
          labels: `Labels: ${labelNames}\n`,
          body: issue.body,
        }
      })
  }

  const addIssueComments = async (issuesToProcess, previousOwner) => {
    return await Promise.all(
      issuesToProcess.map(async (issue) => {
        let issueComments
        try {
          issueComments = await octokit.rest.issues.listComments({
            owner: previousOwner,
            repo: issue.repo,
            issue_number: issue.issueNumber,
          })
        } catch (err) {
          console.log(
            'Could not get the comments for issue ' + issue.issueNumber
          )
          return issue
        }
        return issueComments.data.length > 0
          ? { ...issue, comments: parseComments(issueComments.data) }
          : issue
      })
    )
  }

  try {
    let issuesToSave
    for (let repo of repos) {
      let rawIssues = await octokit.paginate(
        'GET /repos/{owner}/{repo}/issues',
        { owner: previousOwner, repo: repo.name, state: 'all' }
      )
      let parsedIssues = parseIssues(rawIssues)
      issuesToSave = await addIssueComments(parsedIssues, previousOwner)
      repo.issues = issuesToSave
    }
    let data = JSON.stringify(repos, null, 4)
    fs.writeFileSync('issues.json', data)
    return repos
  } catch (err) {
    console.error('Could not parse all issues due to ' + err)
  }
}

async function transferIssues(REPOS, previousOwner, newOwner, targetLabel) {
  const issuesFile = 'issues.json'
  let repos = fs.existsSync(issuesFile)
    ? JSON.parse(fs.readFileSync('issues.json', 'utf-8'))
    : await getTargetIssues(previousOwner, targetLabel, REPOS)

  repos.forEach((repo) => {
    repo.issues.forEach(async (issue) => {
      const issueMeta = `${issue.migrationNotice}\n\`\`\`\n${[
        issue.author,
        issue.date,
        issue.labels,
      ].join('')}\`\`\``
      const commentsToAdd = issue.comments
        ? `\n--------\r\n### Original Comments: \n\n${issue.comments.join(
            '\n\n'
          )}`
        : ''
      try {
        await octokit.rest.issues.create({
          owner: newOwner,
          repo: repo.a8cName,
          title: issue.title,
          body: [issueMeta, issue.body].join('\r\n') + commentsToAdd,
        })
      } catch (e) {
        console.error(
          `Could not create an issue "${issue.title}" in ${repo.a8cName} due to ${e}`
        )
      }
    })
  })
}

const REPOS = [
  {
    name: 'cccatalog-frontend',
    fullName: 'CC Search Frontend repository',
    a8cName: 'ccsearch-frontend',
  },
  {
    name: 'cccatalog-api',
    fullName: 'CC Search API repository',
    a8cName: 'ccsearch-api',
  },
  {
    name: 'cccatalog',
    fullName: 'CC Search Catalog repository',
    a8cName: 'ccsearch-catalog',
  },
]
// We will only use the issues with this label
const LABEL = '🙅 status: discontinued'
// The issues will be transferred from `OLD_ORG` organization to the `NEW_ORG` organization
const OLD_ORG = 'creativecommons'
const NEW_ORG = 'Automattic'

transferIssues(REPOS, OLD_ORG, NEW_ORG, LABEL)
