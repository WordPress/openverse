import { readFileSync } from 'fs'
import { PullRequest } from './utils/pr.mjs'
import { IdSet } from './utils/id_set.mjs'

const exactlyOne = ['priority', 'goal']
const atleastOne = ['aspect']
const atleastOneCheckOnly = ['stack']

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
  for (let req of atleastOne + atleastOneCheckOnly) {
    if (labels.filter((label) => label.name.includes(req)).length < 1) {
      return false
    }
  }
  return true
}

/**
 * Apply labels to a PR based on the PR's linked issues.
 *
 * Note that this function does not concern itself with the management of stack
 * labels as that is performed by a job in the CI + CD workflow.
 *
 * @param octokit {import('@octokit/rest').Octokit} the Octokit instance to use
 * @param core {import('@actions/core')} GitHub Actions toolkit, for logging
 */
export const main = async (octokit, core) => {
  const { eventName, eventAction, prNodeId } = JSON.parse(
    readFileSync('/tmp/event.json', 'utf-8')
  )

  if (
    eventName !== 'pull_request' ||
    !['opened', 'edited'].includes(eventAction)
  ) {
    core.info('This is not an event where a PR should be labelled.')
    return
  }

  const pr = new PullRequest(octokit, core, prNodeId)
  await pr.init()

  let isTriaged = false
  if (pr.labels && pr.labels.some((label) => !label.name.includes('stack'))) {
    // If a PR has non-stack labels, it has likely been triaged by a maintainer.
    core.info('The PR already has non-stack labels.')
    isTriaged = true
  }

  // The logic for labelling a PR is as follows.
  const finalLabels = new IdSet()

  // We start with the PRs current labels. We do not remove any labels already
  // set as they could be the work of the CI labeller job or a maintainer.
  pr.labels.forEach((label) => {
    core.debug(`Adding label "${label.name}" from PR.`)
    finalLabels.add(label)
  })

  // Then we compile all the labels of all the linked issues into a pool. This
  // will be used to find the labels that satisfy the requirements.
  const labelPool = pr.linkedIssues.flatMap((issue) => issue.labels)
  core.debug(`Label pool: ${labelPool}`)

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
    core.info(`Adding labels "${validLabels}" to PR.`)
    validLabels.forEach((label) => {
      finalLabels.add(label)
    })
  }

  // We check if the label is fully labeled. If not, we add the appropriate
  // label to get the maintainers' attention.
  if (!getIsFullyLabeled(finalLabels.items)) {
    let attnLabel
    if (isTriaged) {
      attnLabel = '🏷 status: label work required'
    } else {
      attnLabel = '🚦 status: awaiting triage'
    }
    core.info(`Pull not fully labelled so adding "${attnLabel}".`)
    finalLabels.add(attnLabel)
  }

  // Finally we commit all label IDs to the PR via a mutation. GitHub will only
  // add the new IDs we provide, no existing label will be changed.
  await pr.addLabels(Array.from(finalLabels.ids))
}

import { Octokit } from '@octokit/rest'
let octokit = new Octokit({ auth: process.env.ACCESS_TOKEN })
let core = { info: console.log }
await main(octokit, core)
