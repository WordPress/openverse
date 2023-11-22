/**
 * This module handles all events related to issues.
 *
 * Invoke it from the CLI with
 * - the event name as the `--event_name` argument
 * - the event action as the `--event_action` argument
 * - the event payload in the `event.json` file in the project root
 */

import { getBoard } from '../utils/projects.mjs'
import { getEvent } from '../utils/event.mjs'

const { eventAction, eventPayload } = getEvent()

if (
  eventPayload.issue.labels.some((label) => label.name === '🧭 project: thread')
) {
  // Do not add project threads to the Backlog board.
  process.exit(0)
}

const backlogBoard = await getBoard('Backlog')
const columns = backlogBoard.columns // computed property

// Create new, or get the existing, card for the current issue.
const card = await backlogBoard.addCard(eventPayload.issue.node_id)

/**
 * Set the "Priority" custom field based on the issue's labels.
 */
const syncPriority = async () => {
  const priority = eventPayload.issue.labels.find((label) =>
    label.name.includes('priority')
  )?.name
  if (priority) {
    await backlogBoard.setCustomChoiceField(card.id, 'Priority', priority)
  }
  if (priority === '🟥 priority: critical') {
    await backlogBoard.moveCard(card.id, columns.ToDo)
  }
}

switch (eventAction) {
  case 'opened':
  case 'reopened':
    if (
      eventPayload.issue.labels.some(
        (label) => label.name === '⛔ status: blocked'
      )
    ) {
      await backlogBoard.moveCard(card.id, columns.Blocked)
    } else {
      await backlogBoard.moveCard(card.id, columns.Backlog)
    }

    await syncPriority()
    break

  case 'closed':
    if (eventPayload.issue.state_reason === 'completed') {
      await backlogBoard.moveCard(card.id, columns.Done)
    } else {
      await backlogBoard.moveCard(card.id, columns.Discarded)
    }
    break

  case 'assigned':
    if (card.status === columns.Backlog) {
      await backlogBoard.moveCard(card.id, columns.ToDo)
    }
    break

  case 'labeled':
    if (eventPayload.label.name === '⛔ status: blocked') {
      await backlogBoard.moveCard(card.id, columns.Blocked)
    }
    await syncPriority()
    break

  case 'unlabeled':
    if (eventPayload.label.name === '⛔ status: blocked') {
      // TODO: Move back to the column it came from.
      await backlogBoard.moveCard(card.id, columns.Backlog)
    }
    await syncPriority()
    break
}
