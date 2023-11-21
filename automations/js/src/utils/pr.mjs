import { getOctokit } from './octokit.mjs'

export class PullRequest {
  constructor(owner, repo, number) {
    this.octokit = getOctokit()
    this.owner = owner
    this.repo = repo
    this.number = number
  }

  async init() {
    const prDetails = await this.getPrDetails()
    this.linkedIssues = prDetails.linkedIssues
    this.reviewDecision = prDetails.reviewDecision
    this.reviewStates = prDetails.reviewStates
  }

  /**
   * Get additional information about the PR such as the linked issues and the
   * review decision, as well the states of all submitted reviews.
   *
   * @returns {Promise<{reviewDecision: 'APPROVED' | 'CHANGES_REQUESTED' | 'REVIEW_REQUIRED', linkedIssues: string[], reviewStates: ('APPROVED' | 'CHANGES_REQUESTED' | 'COMMENTED' | 'DISMISSED' | 'PENDING')[]}>}
   */
  async getPrDetails() {
    const res = await this.octokit.graphql(
      `query getPrDetails($owner: String!, $repo: String!, $number: Int!) {
        repository(owner: $owner, name: $repo) {
          pullRequest(number: $number) {
            reviewDecision
            closingIssuesReferences(first: 10) {
              nodes {
                id
              }
            }
            reviews(first: 100) {
              nodes {
                state
              }
            }
          }
        }
      }`,
      {
        owner: this.owner,
        repo: this.repo,
        number: this.number,
      }
    )
    const pr = res.repository.pullRequest
    return {
      reviewDecision: pr.reviewDecision,
      linkedIssues: pr.closingIssuesReferences.nodes.map((node) => node.id),
      reviewStates: pr.reviews.nodes.map((node) => node.state),
    }
  }

  /**
   * Get the count of each type of PR reviews.
   *
   * @returns {{APPROVED: number, COMMENTED: number, CHANGES_REQUESTED: number, DISMISSED: number, PENDING: number}} the PR review counts
   */
  get reviewCounts() {
    const reviewCounts = {
      APPROVED: 0,
      COMMENTED: 0,
      CHANGES_REQUESTED: 0,
      DISMISSED: 0,
      PENDING: 0,
    }
    for (let reviewState of this.reviewStates) {
      reviewCounts[reviewState] += 1
    }
    return reviewCounts
  }
}
