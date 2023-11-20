import { getOctokit } from './octokit.mjs'

export class PullRequest {
  constructor(pullRequest) {
    this.octokit = getOctokit()
    this.pullRequest = pullRequest
  }

  /**
   * Get the count of each type of PR reviews.
   *
   * @returns {Promise<{APPROVED: number, COMMENTED: number, CHANGES_REQUESTED: number}>} the PR review counts
   */
  async reviewCounts() {
    const reviewCounts = {
      APPROVED: 0,
      COMMENTED: 0,
      CHANGES_REQUESTED: 0,
    }

    const { data: reviews } = await this.octokit.rest.pulls.listReviews({
      owner: this.pullRequest.base.user.login,
      repo: this.pullRequest.base.repo.name,
      pull_number: this.pullRequest.number,
    })
    for (let review of reviews) {
      reviewCounts[review.state] += 1
    }
    return reviewCounts
  }
}
