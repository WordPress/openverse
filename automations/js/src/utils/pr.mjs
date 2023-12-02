/**
 * the final decision on the PR from combining all reviews
 * @typedef {'APPROVED' | 'CHANGES_REQUESTED' | 'REVIEW_REQUIRED'} ReviewDecision
 *
 * the state of a particular review left on a PR
 * @typedef {'APPROVED' | 'CHANGES_REQUESTED' | 'COMMENTED' | 'DISMISSED' | 'PENDING'} ReviewState
 *
 * a tag applied to an issue or a PR
 * @typedef {{id: string, name: string}} Label
 *
 * the linked issue of a PR
 * @typedef {{id: string, labels: Label[]}} Issue
 *
 * the additional information about the PR obtained from a GraphQL query
 * @typedef {{
 *   isMerged: boolean,
 *   isDraft: boolean,
 *   reviewDecision: ReviewDecision,
 *   linkedIssues: Issue[],
 *   reviewStates: ReviewState[],
 *   labels: Label[],
 * }} PrDetails
 */

export class PullRequest {
  /**
   * Create a new `PullRequest` instance. This takes the `node_id` of the PR
   * as opposed to the conventional `id` or `number` fields.
   *
   * @param octokit {import('@octokit/rest').Octokit} the Octokit instance to use
   * @param nodeId {boolean} the `node_id` of the PR for GraphQL requests
   */
  constructor(octokit, nodeId) {
    this.octokit = octokit

    this.nodeId = nodeId
  }

  /**
   * Initialise the PR and populate fields that require API call to GitHub.
   */
  async init() {
    const prDetails = await this.getPrDetails()
    Object.assign(this, prDetails)
  }

  /**
   * Get additional information about the PR such as the linked issues and the
   * review decision, as well the states of all submitted reviews.
   *
   * @returns {Promise<PrDetails>}
   */
  async getPrDetails() {
    const res = await this.octokit.graphql(
      `query getPrDetails($id: ID!) {
        node(id: $id) {
          ... on PullRequest {
            isDraft
            merged
            reviewDecision
            labels(first: 20) {
              nodes {
                id
                name
              }
            }
            closingIssuesReferences(first: 10) {
              nodes {
                id
                labels(first: 20) {
                  nodes {
                    id
                    name
                  }
                }
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
        id: this.nodeId,
      }
    )
    const pr = res.node
    return {
      isMerged: pr.isMerged,
      isDraft: pr.merged,
      reviewDecision: pr.reviewDecision,
      linkedIssues: pr.closingIssuesReferences.nodes.map((node) => ({
        id: node.id,
        labels: node.labels.nodes,
      })),
      reviewStates: pr.reviews.nodes.map((node) => node.state),
      labels: pr.labels.nodes,
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
