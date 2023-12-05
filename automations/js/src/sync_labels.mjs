/**
 * a tag applied to an issue or label
 * @typedef {{name: string, color: string, description: string}} Label
 */

const infraRepo = {
  owner: 'WordPress',
  repo: 'openverse-infrastructure',
}

const monoRepo = {
  owner: 'WordPress',
  repo: 'openverse',
}

const exclusions = [/^design:/, /^migrations$/]

/**
 * Compare two labels and list the aspects that are different.
 * @param a {Label} the first label to compare with the second
 * @param b {Label} the second label to compare with the first
 * @returns {string[]} a list of differences between the two labels
 */
const cmpLabels = (a, b) => {
  const differences = []
  if (a.description !== b.description) {
    differences.push('description')
  }
  if (a.color !== b.color) {
    differences.push('color')
  }
  return differences
}

/**
 * Non-destructively update labels in the `WordPress/openverse-infrastructure`
 * repo using the Openverse monorepo as the source of truth.
 *
 * - Excluded labels from the monorepo will not be synced.
 * - Labels with the same name will be updated to match description and color.
 * - Monorepo labels not present in the infrastructure repo will be created.
 * - Any extra labels in the infrastructure repo will be unchanged.
 *
 * @param octokit {import('@octokit/rest').Octokit} the Octokit instance to use
 * @param core {import('@actions/core')} GitHub Actions toolkit, for logging
 */
export const main = async (octokit, core) => {
  // We assume that both repos have < 100 labels and do not paginate.

  /** @type {Label[]} */
  const { data: monoLabels } = await octokit.issues.listLabelsForRepo({
    ...monoRepo,
    per_page: 100,
  })

  core.info(`Found ${monoLabels.length} labels in the monorepo.`)

  /** @type {Label[]} */
  const { data: infraLabels } = await octokit.issues.listLabelsForRepo({
    ...infraRepo,
    per_page: 100,
  })

  core.info(`Found ${infraLabels.length} labels in the infrastructure repo.`)

  /** @type {{[p: string]: Label}} */
  const infraLabelMap = Object.fromEntries(
    infraLabels.map((label) => [label.name, label])
  )

  for (let label of monoLabels) {
    if (exclusions.some((rule) => label.name.match(rule))) {
      core.info(`Label "${label.name}" is excluded from sync.`)
      continue
    }

    const newLabel = {
      ...infraRepo,
      name: label.name,
      description: label.description,
      color: label.color,
    }

    const infraLabel = infraLabelMap[label.name]
    if (infraLabel) {
      const diff = cmpLabels(label, infraLabel)
      if (diff.length) {
        const diffs = diff.join(', ')
        core.info(`Label "${label.name}" differs in ${diffs}. Updating.`)
        await octokit.issues.updateLabel(newLabel)
      }
    } else {
      core.info(`Label "${label.name}" does not exist. Creating.`)
      await octokit.issues.createLabel(newLabel)
    }
  }
}
