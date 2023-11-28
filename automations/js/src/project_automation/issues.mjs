import { getBoard } from '../utils/projects.mjs'

/**
 * Set the "Priority" custom field based on the issue's labels. Also move
 * the card for critical issues directly to the "📅 To Do" column.
 *
 * @param issue {import('@octokit/rest')}
 * @param board {import('../utils/projects.mjs').Project}
 * @param card {import('../utils/projects.mjs').Card}
 * @param core {import('@actions/core')} for logging
 */
async function syncPriority(issue, board, card, core) {
  core.debug(`Starting syncPriority for issue: ${issue.number}`)
  const priority = issue.labels.find((label) =>
    label.name.includes('priority')
  )?.name

  if (priority) {
    await board.setCustomChoiceField(card.id, 'Priority', priority, core)
  }
  if (priority === '🟥 priority: critical') {
    await board.moveCard(card.id, board.columns.ToDo, core)
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
  const { EVENT_ACTION: eventAction } = process.env

  core.debug(`Event action received: ${eventAction}`)

  const issue = context.payload.issue
  const label = context.payload.label
  core.info('Issue details:', issue)

  if (issue.labels.some((label) => label.name === '🧭 project: thread')) {
    core.warning('Issue is a project thread. Exiting.')
    process.exit(0)
  }

  await core.group('Processing Issue or PR', async () => {
    core.debug('Getting instance for the project')
    const backlogBoard = await getBoard(octokit, 'Backlog')

    core.debug('Adding the issue or PR to the project')
    const card = await backlogBoard.addCard(issue.node_id)

    switch (eventAction) {
      case 'opened':
      case 'reopened':
        core.info('Issue opened or reopened')
        if (issue.labels.some((label) => label.name === '⛔ status: blocked')) {
          await backlogBoard.moveCard(
            card.id,
            backlogBoard.columns.Blocked,
            core
          )
        } else {
          await backlogBoard.moveCard(
            card.id,
            backlogBoard.columns.Backlog,
            core
          )
        }
        await syncPriority(issue, backlogBoard, card, core)
        break

      case 'closed':
        core.info('Issue closed')
        if (issue.state_reason === 'completed') {
          await backlogBoard.moveCard(card.id, backlogBoard.columns.Done, core)
        } else {
          await backlogBoard.moveCard(
            card.id,
            backlogBoard.columns.Discarded,
            core
          )
        }
        break

      case 'assigned':
        core.info('Issue assigned')
        if (card.status === backlogBoard.columns.Backlog) {
          await backlogBoard.moveCard(card.id, backlogBoard.columns.ToDo, core)
        }
        break

      case 'labeled':
        core.info(`Issue labeled: ${label.name}`)
        if (label.name === '⛔ status: blocked') {
          await backlogBoard.moveCard(
            card.id,
            backlogBoard.columns.Blocked,
            core
          )
        }
        await syncPriority(issue, backlogBoard, card, core)
        break

      case 'unlabeled':
        core.info(`Label removed: ${label.name}`)
        if (label.name === '⛔ status: blocked') {
          await backlogBoard.moveCard(
            card.id,
            backlogBoard.columns.Backlog,
            core
          )
        }
        await syncPriority(issue, backlogBoard, card, core)
        break
    }
  })
}
