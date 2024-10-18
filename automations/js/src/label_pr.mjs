import { readFileSync } from "fs"

import { PullRequest } from "./utils/pr.mjs"
import { IdSet } from "./utils/id_set.mjs"

const exactlyOne = ["priority", "goal"]
const atleastOne = ["aspect", "stack"]

const pathLabels = {
  migrations: "migrations",
  project_proposal: "🧭 project: proposal",
  project_ip: "🧭 project: implementation plan",
}

/**
 * Get the list of labels that are applicable to a PR based on the changes.
 *
 * @param allLabels  {import('./utils/pr.mjs').Label[]} list of all labels in the repo
 * @param changes {string[]} the list of groups that are changed by the PR
 * @returns {import('./utils/pr.mjs').Label[]} the labels for the PR based on changes
 */
function getLabelsFromChanges(allLabels, changes) {
  const applicableLabels = allLabels
    .filter((label) => label.name.startsWith("🧱 stack:"))
    .filter((label) => {
      const [, stackName] = label.name.split(": ")
      return changes.includes(stackName)
    })
  Object.entries(pathLabels).forEach(([group, labelName]) => {
    if (changes.includes(group)) {
      applicableLabels.push(allLabels.find((label) => label.name === labelName))
    }
  })
  return applicableLabels
}

/**
 * Check if the list of labels covers all requirements.
 *
 * @param labels {import('./utils/pr.mjs').Label[]} the list of labels
 * @returns {boolean} whether the list of labels covers all requirements
 */
function getIsFullyLabeled(labels) {
  for (let req of exactlyOne) {
    if (labels.filter((label) => label.name.includes(req)).length !== 1) {
      return false
    }
  }
  for (let req of atleastOne) {
    if (labels.filter((label) => label.name.includes(req)).length < 1) {
      return false
    }
  }
  return true
}

/**
 * Get all `Label` instances for a repository.
 *
 * @param octokit {import('@octokit/rest').Octokit} the Octokit instance to use
 * @param repository {string} the full name of the repository, including owner
 * @returns {import('./utils/pr.mjs').Label[]} the label with the `id` and `name` fields
 */
async function getAllLabels(octokit, repository) {
  const [owner, repo] = repository.split("/")
  const res = await octokit.rest.issues.listLabelsForRepo({
    owner,
    repo,
    per_page: 100,
  })
  return res.data.map((item) => ({
    id: item.node_id,
    name: item.name,
  }))
}

/**
 * Apply labels to a PR based on the PR's linked issues.
 *
 * @param octokit {import('@octokit/rest').Octokit} the Octokit instance to use
 * @param core {import('@actions/core')} GitHub Actions toolkit, for logging
 */
export const main = async (octokit, core) => {
  const { GITHUB_REPOSITORY } = process.env
  const { eventName, eventAction, prNodeId } = JSON.parse(
    readFileSync("/tmp/event.json", "utf-8")
  )
  const changes = JSON.parse(readFileSync("/tmp/change.json", "utf-8"))

  const allLabels = await getAllLabels(octokit, GITHUB_REPOSITORY)

  if (
    eventName !== "pull_request" ||
    !["opened", "edited"].includes(eventAction)
  ) {
    core.info(
      `Event "${eventName}"/"${eventAction}" is not an event where a PR should be labelled.`
    )
    return
  }

  const pr = new PullRequest(octokit, core, prNodeId)
  await pr.init()

  let isTriaged = false
  if (pr.labels.length) {
    // If a PR already has some labels, it is considered triaged.
    core.info("The PR already has some labels.")
    isTriaged = true
  }

  // The logic for labelling a PR is as follows.
  const finalLabels = new IdSet()

  // We start with the PRs current labels. We do not remove any labels already
  // set as they could be the work of a maintainer.
  pr.labels.forEach((label) => {
    core.debug(`Retaining label "${label.name}" from PR.`)
    finalLabels.add(label)
  })

  // Here we determine the labels from the groups changed by the PR. This
  // consists of stack labels and some very specific labels based on file paths.
  getLabelsFromChanges(allLabels, changes).forEach((label) => {
    core.info(`Adding change-based label "${label.name}" to PR.`)
    finalLabels.add(label)
  })

  // Then we compile all the labels of all the linked issues into a pool. This
  // will be used to find the labels that satisfy the requirements.
  const labelPool = pr.linkedIssues.flatMap((issue) => issue.labels)
  core.debug(`Label pool: ${labelPool.map((label) => label.name).join(",")}`)

  // For each label that we only need one of, we check if the PR already has
  // such a label. If not, we check if the label pool contains any valid labels
  // and add the first one we find.
  for (let rule of exactlyOne) {
    if (finalLabels.items.some((label) => label.name.includes(rule))) {
      core.info(`PR already has a "${rule}" label.`)
      continue
    }
    const validLabel = labelPool.find((label) => label.name.includes(rule))
    if (validLabel) {
      core.info(`Adding label "${validLabel.name}" to PR.`)
      finalLabels.add(validLabel)
    }
  }

  // For each label that we need at least one of, we add all the valid labels
  // from the label pool. Our ID set implementation will weed out duplicates.
  for (let rule of atleastOne) {
    const validLabels = labelPool.filter((label) => label.name.includes(rule))
    core.info(
      `Adding labels "${validLabels
        .map((label) => label.name)
        .join(",")}" to PR.`
    )
    validLabels.forEach((label) => {
      finalLabels.add(label)
    })
  }

  // We check if the label is fully labeled. If not, we add the appropriate
  // label to get the maintainers' attention.
  if (!getIsFullyLabeled(finalLabels.items)) {
    let attnLabel
    if (isTriaged) {
      attnLabel = "🏷 status: label work required"
    } else {
      attnLabel = "🚦 status: awaiting triage"
    }
    core.info(`PR not fully labelled so adding "${attnLabel}".`)
    attnLabel = allLabels.filter((item) => item.name === attnLabel)[0]
    finalLabels.add(attnLabel)
  }

  // Finally we commit all label IDs to the PR via a mutation. GitHub will only
  // add the new IDs we provide, no existing label will be changed.
  await pr.addLabels(Array.from(finalLabels.ids))
}
