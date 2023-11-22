import { readFileSync } from 'fs'

import { getBoard } from '../utils/projects.mjs'
import { PullRequest } from '../utils/pr.mjs'

/**
 * This is the entrypoint of the script.
 *
 * @param octokit {import('@octokit/rest').Octokit} the Octokit instance to use
 */
export const main = async (octokit) => {
  const { eventName, eventAction } = JSON.parse(
    readFileSync('/tmp/event_info.json', 'utf-8')
  )
  const eventPayload = JSON.parse(readFileSync('/tmp/event.json', 'utf-8'))

  const pr = new PullRequest(octokit, eventPayload.pull_request.node_id)
  await pr.init()

  const prBoard = await getBoard(octokit, 'PRs')
  const prColumns = prBoard.columns // computed property

  const backlogBoard = await getBoard(octokit, 'Backlog')
  const backlogColumns = backlogBoard.columns

  // Create new, or get the existing, card for the current pull request.
  const card = await prBoard.addCard(pr.nodeId)

  /**
   * Move the PR to the right column based on the number of reviews.
   */
  const syncReviews = async () => {
    const reviewDecision = pr.reviewDecision
    const reviewCounts = pr.reviewCounts

    if (reviewDecision === 'APPROVED') {
      await prBoard.moveCard(card.id, prColumns.Approved)
    } else if (reviewDecision === 'CHANGES_REQUESTED') {
      await prBoard.moveCard(card.id, prColumns.ChangesRequested)
    } else if (reviewCounts.APPROVED === 1) {
      await prBoard.moveCard(card.id, prColumns.Needs1Review)
    } else {
      await prBoard.moveCard(card.id, prColumns.Needs2Reviews)
    }
  }

  /**
   * Move all linked issues to the specified column.
   */
  const syncIssues = async (destColumn) => {
    for (let linkedIssue of pr.linkedIssues) {
      const card = await backlogBoard.addCard(linkedIssue)
      await backlogBoard.moveCard(card.id, destColumn)
    }
  }

  if (eventName === 'pull_request_review') {
    await syncReviews()
  } else if (eventName === 'pull_request_target') {
    switch (eventAction) {
      case 'opened':
      case 'reopened': {
        if (pr.isDraft) {
          await prBoard.moveCard(card.id, prColumns.Draft)
        } else {
          await syncReviews()
        }
        await syncIssues(backlogColumns.InProgress)
        break
      }

      case 'edited': {
        await syncIssues(backlogColumns.InProgress)
        break
      }

      case 'converted_to_draft': {
        await prBoard.moveCard(card.id, prColumns.Draft)
        break
      }

      case 'ready_for_review': {
        await syncReviews()
        break
      }

      case 'closed': {
        if (!pr.isMerged) {
          await syncIssues(backlogColumns.Backlog)
        }
        break
      }
    }
  }
}
