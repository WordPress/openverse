// const github = require('@actions/github')
const core = require('@actions/core')

async function run() {
  const isDryRun = core.getBooleanInput('dry_run') ?? false
  core.info(`Dry run status: ${isDryRun}`)
  core.info('Success.')
  return true
}

run()
