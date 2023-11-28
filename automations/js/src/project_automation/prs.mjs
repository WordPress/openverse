import { readFileSync } from 'fs'

import { getBoard } from '../utils/projects.mjs'
import { PullRequest } from '../utils/pr.mjs'

async function syncReviews(pr, prBoard, prCard, core) {
  core.debug(`Synchronizing reviews for PR: ${pr.nodeId}`)
  const reviewDecision = pr.reviewDecision
  core.debug(`Review decision: ${reviewDecision}`)

  await core.group(
    `Handling review decision for PR: ${pr.nodeId}`,
    async () => {
      if (reviewDecision === 'APPROVED') {
        await prBoard.moveCard(prCard.id, prBoard.columns.Approved, core)
      } else if (reviewDecision === 'CHANGES_REQUESTED') {
        await prBoard.moveCard(
          prCard.id,
          prBoard.columns.ChangesRequested,
          core
        )
      } else if (pr.reviewCounts.APPROVED === 1) {
        await prBoard.moveCard(prCard.id, prBoard.columns.Needs1Review, core)
      } else {
        await prBoard.moveCard(prCard.id, prBoard.columns.Needs2Reviews, core)
      }
    }
  )
}

async function syncIssues(pr, backlogBoard, destColumn, core) {
  core.debug(`Synchronizing linked issues for PR: ${pr.nodeId}`)
  for (let linkedIssue of pr.linkedIssues) {
    await core.group(`Processing linked issue: ${linkedIssue}`, async () => {
      core.debug('Adding linked issue to board')
      const issueCard = await backlogBoard.addCard(linkedIssue)
      await backlogBoard.moveCard(
        issueCard.id,
        backlogBoard.columns[destColumn],
        core
      )
    })
  }
}

/**
 * This is the entrypoint of the script.
 *
 * @param octokit {import('@octokit/rest').Octokit} the Octokit instance to use
 * @param context {import('@actions/github').context} info about the current event
 * @param core {import('@actions/core')} Core functions for setting results, logging, registering secrets and exporting variables across actions
 */
export const main = async (octokit, context, core) => {
  core.debug('Starting PR script')

  const { eventName, eventAction, prNodeId } = JSON.parse(
    readFileSync('/tmp/event.json', 'utf-8')
  )
  core.debug(
    `Event details - Name: ${eventName}, Action: ${eventAction}, PR Node ID: ${prNodeId}`
  )

  const pr = new PullRequest(octokit, prNodeId)
  await pr.init()

  const prBoard = await getBoard(octokit, 'PRs')
  const backlogBoard = await getBoard(octokit, 'Backlog')

  const prCard = await prBoard.addCard(pr.nodeId)
  core.debug(`PR card created or fetched: ${prCard.id}`)

  await core.group('Processing PR based on event action', async () => {
    if (eventName === 'pull_request_review') {
      await syncReviews(pr, prBoard, prCard)
    } else {
      switch (eventAction) {
        case 'opened':
        case 'reopened': {
          core.debug('PR opened or reopened')
          if (pr.isDraft) {
            await prBoard.moveCard(prCard.id, prBoard.columns.Draft, core)
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
          await prBoard.moveCard(prCard.id, prBoard.columns.Draft, core)
          break
        }
        case 'ready_for_review': {
          core.debug('PR ready for review')
          await syncReviews(pr, prBoard, prCard)
          break
        }
        case 'closed': {
          core.debug('PR closed')
          if (!pr.isMerged) {
            await syncIssues(pr, backlogBoard, 'Backlog')
          }
          break
        }
      }
    }
  })
}
