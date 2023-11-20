import { dirname, resolve } from 'path'
import { fileURLToPath } from 'url'
import { readFileSync } from 'fs'

import yargs from 'yargs'
import { hideBin } from 'yargs/helpers'

/**
 * Get all information about an event. This combines information received from
 * the CLI arguments and the event payload JSON file.
 *
 * @returns {{eventData: unknown, eventName: string, eventAction: string}} the event information
 */
export function getEvent() {
  const { event_name: eventName, event_action: eventAction } = yargs(
    hideBin(process.argv)
  )
    .help()
    .version(false)
    .option('event_name', {
      type: 'string',
      description: 'the GitHub event that triggered the workflow',
      demandOption: true,
    })
    .option('event_action', {
      type: 'string',
      description: 'the GitHub event action that triggered the workflow',
      demandOption: true,
    })
    .parse()

  return {
    eventName,
    eventAction,
    eventPayload: getEventPayload(),
  }
}

/**
 * Get the event payload from the `github.event` context. This payload must be
 * saved to an `event.json` file in the project root beforehand.
 *
 * @returns {any} the payload from the `github.event` context
 */
function getEventPayload() {
  const thisFile = import.meta.url
  const projectRoot = dirname(dirname(dirname(fileURLToPath(thisFile))))
  const eventJson = resolve(projectRoot, 'event.json')
  return JSON.parse(readFileSync(eventJson, 'utf8'))
}
