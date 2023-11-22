/**
 * the final decision on the PR from combining all reviews
 * @typedef {'APPROVED' | 'CHANGES_REQUESTED' | 'REVIEW_REQUIRED'} ReviewDecision
 *
 * the state of a particular review left on a PR
 * @typedef {'APPROVED' | 'CHANGES_REQUESTED' | 'COMMENTED' | 'DISMISSED' | 'PENDING'} ReviewState
 *
 * the additional information about the PR obtained from a GraphQL query
 * @typedef {{reviewDecision: ReviewDecision, linkedIssues: string[], reviewStates: ReviewState[]}} PrDetails
 */

export class PullRequest {
  /**
   * Create a new `PullRequest` instance using owner and repo names and PR
   * number, all three of which can be found in the PR URL.
   *
   * https://github.com/WordPress/openverse/pull/3375
   *                    ^^^^^^^^^ ^^^^^^^^^^     ^^^^
   *                    owner     repo           number
   *
   * @param octokit {import('octokit').Octokit} the Octokit instance to use
   * @param owner {string} the login of the owner (org) of the project
   * @param repo {string} the name of the repository
   * @param number {number} the number of the project
   */
  constructor(octokit, owner, repo, number) {
    this.octokit = octokit

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
   * @returns {Promise<PrDetails>}
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
   * @returns {{[p: ReviewState]: number}} the PR review counts
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
