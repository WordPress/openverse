import { dirname, resolve } from 'path'
import { fileURLToPath } from 'url'
import { readFileSync } from 'fs'

/**
 * Get the event payload from the `github.event` context. This payload must be
 * saved to an `event.json` file in the project root beforehand.
 *
 * @returns {any} the payload from the `github.event` context
 */
export function getEventData() {
  const thisFile = import.meta.url
  const projectRoot = dirname(dirname(dirname(fileURLToPath(thisFile))))
  const eventJson = resolve(projectRoot, 'event.json')
  return JSON.parse(readFileSync(eventJson, 'utf8'))
}
