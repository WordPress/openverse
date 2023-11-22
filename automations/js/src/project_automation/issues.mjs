import { getBoard } from '../utils/projects.mjs'

/**
 * Set the "Priority" custom field based on the issue's labels. Also move
 * the card for critical issues directly to the "📅 To Do" column.
 *
 * @param issue {import('@octokit/rest')}
 * @param board {import('../utils/projects.mjs').Project}
 * @param card {import('../utils/projects.mjs').Card}
 */
async function syncPriority(issue, board, card) {
  const priority = issue.labels.find((label) =>
    label.name.includes('priority')
  )?.name
  if (priority) {
    await board.setCustomChoiceField(card.id, 'Priority', priority)
  }
  if (priority === '🟥 priority: critical') {
    await board.moveCard(card.id, board.columns.ToDo)
  }
}

/**
 * This is the entrypoint of the script.
 *
 * @param octokit {import('@octokit/rest').Octokit} the Octokit instance to use
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

  // Create new, or get the existing, card for the current issue.
  const card = await backlogBoard.addCard(issue.node_id)

  switch (eventAction) {
    case 'opened':
    case 'reopened': {
      if (issue.labels.some((label) => label.name === '⛔ status: blocked')) {
        await backlogBoard.moveCard(card.id, backlogBoard.columns.Blocked)
      } else {
        await backlogBoard.moveCard(card.id, backlogBoard.columns.Backlog)
      }

      await syncPriority(issue, backlogBoard, card)
      break
    }

    case 'closed': {
      if (issue.state_reason === 'completed') {
        await backlogBoard.moveCard(card.id, backlogBoard.columns.Done)
      } else {
        await backlogBoard.moveCard(card.id, backlogBoard.columns.Discarded)
      }
      break
    }

    case 'assigned': {
      if (card.status === backlogBoard.columns.Backlog) {
        await backlogBoard.moveCard(card.id, backlogBoard.columns.ToDo)
      }
      break
    }

    case 'labeled': {
      if (label.name === '⛔ status: blocked') {
        await backlogBoard.moveCard(card.id, backlogBoard.columns.Blocked)
      }
      await syncPriority(issue, backlogBoard, card)
      break
    }

    case 'unlabeled': {
      if (label.name === '⛔ status: blocked') {
        // TODO: Move back to the column it came from.
        await backlogBoard.moveCard(card.id, backlogBoard.columns.Backlog)
      }
      await syncPriority(issue, backlogBoard, card)
      break
    }
  }
}
