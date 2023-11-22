import { getBoard } from '../utils/projects.mjs'

/**
 * This is the entrypoint of the script.
 *
 * @param octokit {import('octokit').Octokit} the Octokit instance to use
 * @param context {import('@actions/github').context} info about the current event
 */
export const main = async (octokit, context) => {
  const { EVENT_ACTION: eventAction } = process.env

  const issue = context.payload.issue
  const label = context.payload.label

  if (issue.labels.some((label) => label.name === '🧭 project: thread')) {
    // Do not add project threads to the Backlog board.
    process.exit(0)
  }

  const backlogBoard = await getBoard(octokit, 'Backlog')
  const columns = backlogBoard.columns // computed property

  // Create new, or get the existing, card for the current issue.
  const card = await backlogBoard.addCard(issue.node_id)

  /**
   * Set the "Priority" custom field based on the issue's labels. Also move
   * the card for critical issues directly to the "📅 To Do" column.
   */
  const syncPriority = async () => {
    const priority = issue.labels.find((label) =>
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
    case 'reopened': {
      if (issue.labels.some((label) => label.name === '⛔ status: blocked')) {
        await backlogBoard.moveCard(card.id, columns.Blocked)
      } else {
        await backlogBoard.moveCard(card.id, columns.Backlog)
      }

      await syncPriority()
      break
    }

    case 'closed': {
      if (issue.state_reason === 'completed') {
        await backlogBoard.moveCard(card.id, columns.Done)
      } else {
        await backlogBoard.moveCard(card.id, columns.Discarded)
      }
      break
    }

    case 'assigned': {
      if (card.status === columns.Backlog) {
        await backlogBoard.moveCard(card.id, columns.ToDo)
      }
      break
    }

    case 'labeled': {
      if (label.name === '⛔ status: blocked') {
        await backlogBoard.moveCard(card.id, columns.Blocked)
      }
      await syncPriority()
      break
    }

    case 'unlabeled': {
      if (label.name === '⛔ status: blocked') {
        // TODO: Move back to the column it came from.
        await backlogBoard.moveCard(card.id, columns.Backlog)
      }
      await syncPriority()
      break
    }
  }
}
