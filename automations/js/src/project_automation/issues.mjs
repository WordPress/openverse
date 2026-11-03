import { getBoard } from "../utils/projects.mjs"

/**
 * Set the "Priority" custom field based on the issue's labels.
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
}

/**
 * Determine the single destination for an issue card.
 *
 * Critical priority takes precedence over blocked status. Label events only
 * move cards when the changed label can affect the destination.
 *
 * @param issue {Issue} the issue for which to determine a destination
 * @param eventAction {string} the issue event action
 * @param changedLabel {object | undefined} the label from the event payload
 * @returns {string | null} the destination column, or null when no move is needed
 */
export function getIssueDestination(issue, eventAction, changedLabel) {
  const isCritical = issue.labels.some(
    (label) => label.name === "🟥 priority: critical"
  )
  const isBlocked = issue.labels.some(
    (label) => label.name === "⛔ status: blocked"
  )
  const changedLabelName = changedLabel?.name

  if (eventAction === "closed") {
    return issue.state_reason === "completed" ? "Done" : "Discarded"
  }

  if (eventAction === "assigned") {
    return null
  }

  if (eventAction === "opened" || eventAction === "reopened") {
    return isCritical ? "ToDo" : isBlocked ? "Blocked" : "Backlog"
  }

  if (eventAction === "labeled" || eventAction === "unlabeled") {
    const changedStatus = changedLabelName === "⛔ status: blocked"
    const changedPriority = changedLabelName === "🟥 priority: critical"

    if (changedStatus || changedPriority) {
      return isCritical ? "ToDo" : isBlocked ? "Blocked" : "Backlog"
    }
  }

  return null
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
      await syncPriority(core, issue, backlogBoard, card)
      const destination = getIssueDestination(issue, eventAction, label)
      await backlogBoard.moveCard(card.id, backlogBoard.columns[destination])
      break
    }

    case "closed": {
      const destination = getIssueDestination(issue, eventAction, label)
      if (destination === "Done") {
        core.info("Issue was closed as completed.")
      } else {
        core.info("Issue was closed as discarded.")
      }
      await backlogBoard.moveCard(card.id, backlogBoard.columns[destination])
      break
    }

    case "assigned": {
      if (card.status === backlogBoard.columns.Backlog) {
        await backlogBoard.moveCard(card.id, backlogBoard.columns.ToDo)
      }
      break
    }

    case "labeled": {
      await syncPriority(core, issue, backlogBoard, card)
      const destination = getIssueDestination(issue, eventAction, label)
      if (destination) {
        await backlogBoard.moveCard(card.id, backlogBoard.columns[destination])
      }
      break
    }

    case "unlabeled": {
      await syncPriority(core, issue, backlogBoard, card)
      const destination = getIssueDestination(issue, eventAction, label)
      if (destination) {
        await backlogBoard.moveCard(card.id, backlogBoard.columns[destination])
      }
      break
    }
  }
}
