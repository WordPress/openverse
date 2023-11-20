import { getOctokit } from './octokit.mjs'

export class PullRequest {
  constructor(owner, repo, number) {
    this.octokit = getOctokit()
    this.owner = owner
    this.repo = repo
    this.number = number
  }

  /**
   * Get the review decision for the given PR.
   *
   * @returns {Promise<string>} one of 'APPROVED', 'CHANGES_REQUESTED' or 'REVIEW_REQUIRED'
   */
  async getReviewDecision() {
    const res = await this.octokit.graphql(
      `query getReviewDecision($owner: String!, $repo: String!, $number: Int!) {
        repository(owner: $owner, name: $repo) {
          pullRequest(number: $number) {
            reviewDecision
          }
        }
      }`,
      {
        owner: this.owner,
        repo: this.repo,
        number: this.number,
      }
    )
    return res.repository.pullRequest.reviewDecision
  }

  /**
   * Get the count of each type of PR reviews.
   *
   * @returns {Promise<{APPROVED: number, COMMENTED: number, CHANGES_REQUESTED: number}>} the PR review counts
   */
  async getReviewCounts() {
    const reviewCounts = {
      APPROVED: 0,
      COMMENTED: 0,
      CHANGES_REQUESTED: 0,
    }

    const { data: reviews } = await this.octokit.rest.pulls.listReviews({
      owner: this.owner,
      repo: this.repo,
      pull_number: this.number,
    })
    for (let review of reviews) {
      reviewCounts[review.state] += 1
    }
    return reviewCounts
  }
}
