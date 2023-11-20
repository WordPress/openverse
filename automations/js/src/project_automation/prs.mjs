/**
 * This module handles all events related to pull requests.
 *
 * Invoke it from the CLI with
 * - the event name as the `--event_name` argument
 * - the event action as the `--event_action` argument
 * - the event payload in the `event.json` file in the project root
 */

import { getBoard } from '../utils/projects.mjs'
import { getEvent } from '../utils/event.mjs'
import { PullRequest } from '../utils/pr.mjs'

const { eventName, eventAction, eventPayload } = getEvent()

const pr = new PullRequest(
  eventPayload.pull_request.base.repo.owner.login,
  eventPayload.pull_request.base.repo.name,
  eventPayload.pull_request.number
)
await pr.init()

const prBoard = await getBoard('PRs')
const columns = prBoard.columns // computed property

// Create new, or get the existing, card for the current pull request.
const card = await prBoard.addCard(eventPayload.pull_request.node_id)

/**
 * Move the PR to the right column based on the number of reviews.
 */
const syncReviews = async () => {
  const reviewDecision = pr.reviewDecision
  const reviewCounts = pr.reviewCounts

  if (reviewDecision === 'APPROVED')
    await prBoard.moveCard(card.id, columns.Approved)
  else if (reviewDecision === 'CHANGES_REQUESTED')
    await prBoard.moveCard(card.id, columns.ChangesRequested)
  else if (reviewCounts.APPROVED === 1)
    await prBoard.moveCard(card.id, columns.Needs1Review)
  else await prBoard.moveCard(card.id, columns.Needs2Reviews)
}

if (eventName === 'pull_request_review') {
  await syncReviews()
} else if (eventName === 'pull_request_target') {
  switch (eventAction) {
    case 'opened':
    case 'reopened':
      if (eventPayload.pull_request.draft)
        await prBoard.moveCard(card.id, columns.Draft)
      else await syncReviews()
      break

    case 'edited':
      // TODO: Handle issue/PR connections.
      break

    case 'converted_to_draft':
      await prBoard.moveCard(card.id, columns.Draft)
      break

    case 'ready_for_review':
      await syncReviews()
      break
  }
}
