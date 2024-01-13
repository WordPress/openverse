import { readFileSync } from 'fs'

import { getBoard } from '../utils/projects.mjs'
import { PullRequest } from '../utils/pr.mjs'

/**
 * Move the PR to the right column based on the number of reviews.
 *
 * @param core {import('@actions/core')} GitHub Actions toolkit, for logging
 * @param pr {PullRequest} the PR to sync with the reviews and decision
 * @param prBoard {Project} the project board for PRs
 * @param prCard {Card} the card for the PR to sync
 */
async function syncReviews(core, pr, prBoard, prCard) {
  core.info(`Synchronizing reviews for PR ${pr.nodeId}.`)

  const reviewDecision = pr.reviewDecision
  const reviewCounts = pr.reviewCounts
  core.debug(`PR review counts: ${reviewCounts}`)
  core.debug(`PR reviews decision: ${reviewDecision}`)

  if (reviewDecision === 'APPROVED') {
    core.info('Moving PR on the basis of review decision.')
    await prBoard.moveCard(prCard.id, prBoard.columns.Approved)
  } else if (reviewDecision === 'CHANGES_REQUESTED') {
    core.info('Moving PR on the basis of review decision.')
    await prBoard.moveCard(prCard.id, prBoard.columns.ChangesRequested)
  } else if (reviewCounts.APPROVED === 1) {
    core.info('Moving PR on the basis of 1 approval.')
    await prBoard.moveCard(prCard.id, prBoard.columns.Needs1Review)
  } else {
    await prBoard.moveCard(prCard.id, prBoard.columns.Needs2Reviews)
  }
}

/**
 * Move all linked issues to the specified column.
 *
 * @param core {import('@actions/core')} GitHub Actions toolkit, for logging
 * @param pr {PullRequest} the PR to sync with the reviews and decision
 * @param backlogBoard {Project} the project board for issues
 * @param destColumn {string} the destination column where to move the issue
 */
async function syncIssues(core, pr, backlogBoard, destColumn) {
  core.info(`Synchronizing issues for PR ${pr.nodeId}.`)

  for (let linkedIssue of pr.linkedIssues) {
    core.info(`Syncing issue ${linkedIssue.id}.`)

    // Create new, or get the existing, card for the current issue.
    const issueCard = await backlogBoard.addCard(linkedIssue.id)
    core.debug(`Issue card ID: ${issueCard.id}`)

    await backlogBoard.moveCard(issueCard.id, backlogBoard.columns[destColumn])
  }
}

/**
 * This is the entrypoint of the script.
 *
 * @param octokit {import('@octokit/rest').Octokit} the Octokit instance to use
 * @param core {import('@actions/core')} GitHub Actions toolkit, for logging
 */
export const main = async (octokit, core) => {
  core.info('Starting script `prs.mjs`.')

  const { eventName, eventAction, prNodeId } = JSON.parse(
    readFileSync('/tmp/event.json', 'utf-8')
  )
  core.debug(`Event name: ${eventName}`)
  core.debug(`Event action: ${eventAction}`)
  core.debug(`PR node ID: ${prNodeId}`)

  const pr = new PullRequest(octokit, core, prNodeId)
  await pr.init()

  const prBoard = await getBoard(octokit, core, 'PRs')
  const backlogBoard = await getBoard(octokit, core, 'Backlog')

  // Create new, or get the existing, card for the current pull request.
  const prCard = await prBoard.addCard(pr.nodeId)
  core.debug(`PR card ID: ${prCard.id}`)

  if (eventName === 'pull_request_review') {
    if (pr.isDraft) {
      await prBoard.moveCard(prCard.id, prBoard.columns.Draft)
    } else {
      await syncReviews(core, pr, prBoard, prCard)
    }
  } else {
    switch (eventAction) {
      case 'opened':
      case 'reopened': {
        if (pr.isDraft) {
          core.info('PR is a draft.')
          await prBoard.moveCard(prCard.id, prBoard.columns.Draft)
        } else {
          core.info('PR is ready for review.')
          await syncReviews(core, pr, prBoard, prCard)
        }
        await syncIssues(core, pr, backlogBoard, 'InProgress')
        break
      }

      case 'edited': {
        await syncIssues(core, pr, backlogBoard, 'InProgress')
        break
      }

      case 'converted_to_draft': {
        await prBoard.moveCard(prCard.id, prBoard.columns.Draft)
        break
      }

      case 'ready_for_review': {
        await syncReviews(core, pr, prBoard, prCard)
        break
      }

      case 'closed': {
        if (!pr.isMerged) {
          core.info('PR was closed without merge.')
          await syncIssues(core, pr, backlogBoard, 'Backlog')
        }
        break
      }
    }
  }
}
