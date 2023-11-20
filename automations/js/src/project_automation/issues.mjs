/**
 * This module handles all events related to issues.
 *
 * Invoke it from the CLI with
 * - the event name as the `--event_name` argument
 * - the event payload in the `EVENT_PAYLOAD` JSON file in the project root
 */

import yargs from 'yargs'
import { hideBin } from 'yargs/helpers'

import { getBoard } from '../utils/projects.mjs'
import { getEventData } from '../utils/event.mjs'

const { event_name: eventName } = yargs(hideBin(process.argv))
  .help()
  .version(false)
  .option('event_name', {
    type: 'string',
    description: 'the GitHub event that triggered the workflow',
    demandOption: true,
  })
  .parse()
console.log('Received event name:', eventName)

// Get more information about the issue from the event payload.
const eventPayload = getEventData()

if (
  eventPayload.issue.labels.some((label) => label.name === '🧭 project: thread')
)
  // Do not add project threads to the Backlog board.
  process.exit(0)

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
  if (priority)
    await backlogBoard.setCustomChoiceField(card.id, 'Priority', priority)
}

switch (eventName) {
  case 'opened':
  case 'reopened':
    if (
      eventPayload.issue.labels.some(
        (label) => label.name === '⛔ status: blocked'
      )
    )
      await backlogBoard.moveCard(card.id, columns.Blocked)
    else await backlogBoard.moveCard(card.id, columns.Backlog)

    await syncPriority()
    break

  case 'closed':
    if (eventPayload.issue.state_reason === 'completed')
      await backlogBoard.moveCard(card.id, columns.Done)
    else await backlogBoard.moveCard(card.id, columns.Discarded)
    break

  case 'assigned':
    if (card.status === columns.Backlog)
      await backlogBoard.moveCard(card.id, columns.Todo)
    break

  case 'labeled':
    if (eventPayload.label.name === '⛔ status: blocked')
      await backlogBoard.moveCard(card.id, columns.Blocked)
    await syncPriority()
    break

  case 'unlabeled':
    if (eventPayload.label.name === '⛔ status: blocked')
      // TODO: Move back to the column it came from.
      await backlogBoard.moveCard(card.id, columns.Backlog)
    await syncPriority()
    break
}
