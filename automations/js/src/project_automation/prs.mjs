import { readFileSync } from 'fs'

import { getBoard } from '../utils/projects.mjs'
import { PullRequest } from '../utils/pr.mjs'

/**
 * Move the PR to the right column based on the number of reviews.
 *
 * @param pr {PullRequest}
 * @param prBoard {Project}
 * @param prCard {Card}
 */
async function syncReviews(pr, prBoard, prCard) {
  const reviewDecision = pr.reviewDecision
  const reviewCounts = pr.reviewCounts

  if (reviewDecision === 'APPROVED') {
    await prBoard.moveCard(prCard.id, prBoard.columns.Approved)
  } else if (reviewDecision === 'CHANGES_REQUESTED') {
    await prBoard.moveCard(prCard.id, prBoard.columns.ChangesRequested)
  } else if (reviewCounts.APPROVED === 1) {
    await prBoard.moveCard(prCard.id, prBoard.columns.Needs1Review)
  } else {
    await prBoard.moveCard(prCard.id, prBoard.columns.Needs2Reviews)
  }
}

/**
 * Move all linked issues to the specified column.
 *
 * @param pr {PullRequest}
 * @param backlogBoard {Project}
 * @param destColumn {string}
 */
async function syncIssues(pr, backlogBoard, destColumn) {
  for (let linkedIssue of pr.linkedIssues) {
    const issueCard = await backlogBoard.addCard(linkedIssue.id)
    await backlogBoard.moveCard(issueCard.id, backlogBoard.columns[destColumn])
  }
}

/**
 * This is the entrypoint of the script.
 *
 * @param octokit {import('@octokit/rest').Octokit} the Octokit instance to use
 */
export const main = async (octokit) => {
  const { eventName, eventAction, prNodeId } = JSON.parse(
    readFileSync('/tmp/event.json', 'utf-8')
  )

  const pr = new PullRequest(octokit, prNodeId)
  await pr.init()

  const prBoard = await getBoard(octokit, 'PRs')
  const backlogBoard = await getBoard(octokit, 'Backlog')

  // Create new, or get the existing, card for the current pull request.
  const prCard = await prBoard.addCard(pr.nodeId)

  if (eventName === 'pull_request_review') {
    await syncReviews(pr, prBoard, prCard)
  } else {
    switch (eventAction) {
      case 'opened':
      case 'reopened': {
        if (pr.isDraft) {
          await prBoard.moveCard(prCard.id, prBoard.columns.Draft)
        } else {
          await syncReviews(pr, prBoard, prCard)
        }
        await syncIssues(pr, backlogBoard, 'InProgress')
        break
      }

      case 'edited': {
        await syncIssues(pr, backlogBoard, 'InProgress')
        break
      }

      case 'converted_to_draft': {
        await prBoard.moveCard(prCard.id, prBoard.columns.Draft)
        break
      }

      case 'ready_for_review': {
        await syncReviews(pr, prBoard, prCard)
        break
      }

      case 'closed': {
        if (!pr.isMerged) {
          await syncIssues(pr, backlogBoard, 'Backlog')
        }
        break
      }
    }
  }
}
