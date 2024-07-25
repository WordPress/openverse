import { getBoard } from "../utils/projects.mjs"

/**
 * Set the "Priority" custom field based on the issue's labels. Also move
 * the card for critical issues directly to the "📅 To Do" column.
 *
 * @param core {import('@actions/core')} GitHub Actions toolkit, for logging
 * @param issue {Issue} the issue for which to set the "Priority" custom field
 * @param backlogBoard {Project} the project board for issues
 * @param issueCard {Card} the card for the issue to sync
 */
async function syncPriority(core, issue, backlogBoard, issueCard) {
  core.info(`Syncing priority for issue "${issue.number}".`)

  const priority = issue.labels.find((label) =>
    label.name.includes("priority")
  )?.name
  core.debug(`Priority: ${priority}`)

  if (priority) {
    await backlogBoard.setCustomChoiceField(issueCard.id, "Priority", priority)
  }
  if (priority === "🟥 priority: critical") {
    core.info('Moving critical issue to "📅 To Do" column.')
    await backlogBoard.moveCard(issueCard.id, backlogBoard.columns.ToDo)
  }
}

/**
 * This is the entrypoint of the script.
 *
 * @param octokit {import('@octokit/rest').Octokit} the Octokit instance to use
 * @param core {import('@actions/core')} GitHub Actions toolkit, for logging
 * @param context {import('@actions/github').context} info about the current event
 */
export const main = async (octokit, core, context) => {
  core.info("Starting script `issues.mjs`.")

  const { EVENT_ACTION: eventAction } = process.env
  core.debug(`Event action: ${eventAction}`)

  const issue = context.payload.issue
  core.debug(`Issue node ID: ${issue.node_id}`)

  const label = context.payload.label
  core.info("Issue details:", issue)

  if (issue.labels.some((label) => label.name === "🧭 project: thread")) {
    core.warning("Issue is a project thread. Exiting.")
    return
  }

  const backlogBoard = await getBoard(octokit, core, "Backlog")

  // Create new, or get the existing, card for the current issue.
  const card = await backlogBoard.addCard(issue.node_id)
  core.debug(`Issue card ID: ${card.id}`)

  switch (eventAction) {
    case "opened":
    case "reopened": {
      if (issue.labels.some((label) => label.name === "⛔ status: blocked")) {
        core.info("Issue was opened, labelled as blocked.")
        await backlogBoard.moveCard(card.id, backlogBoard.columns.Blocked)
      } else {
        await backlogBoard.moveCard(card.id, backlogBoard.columns.Backlog)
      }
      await syncPriority(core, issue, backlogBoard, card)
      break
    }

    case "closed": {
      if (issue.state_reason === "completed") {
        core.info("Issue was closed as completed.")
        await backlogBoard.moveCard(card.id, backlogBoard.columns.Done)
      } else {
        core.info("Issue was closed as discarded.")
        await backlogBoard.moveCard(card.id, backlogBoard.columns.Discarded)
      }
      break
    }

    case "assigned": {
      if (card.status === backlogBoard.columns.Backlog) {
        await backlogBoard.moveCard(card.id, backlogBoard.columns.ToDo)
      }
      break
    }

    case "labeled": {
      if (label.name === "⛔ status: blocked") {
        core.info("Issue was labeled as blocked.")
        await backlogBoard.moveCard(card.id, backlogBoard.columns.Blocked)
      }
      await syncPriority(core, issue, backlogBoard, card)
      break
    }

    case "unlabeled": {
      if (label.name === "⛔ status: blocked") {
        core.info("Issue was unlabeled as blocked.")
        await backlogBoard.moveCard(card.id, backlogBoard.columns.Backlog)
      }
      await syncPriority(core, issue, backlogBoard, card)
      break
    }
  }
}
