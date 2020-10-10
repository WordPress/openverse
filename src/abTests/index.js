import { JOINED_AB_TEST_EXPERIMENT } from '~/store-modules/mutation-types'
import donationLanguage from '~/abTests/experiments/donationLanguage'
import getCookieValue from '~/utils/cookies'
import createSixpackSession from '~/abTests/lib/createSixpackSession'

/**
 * @typedef {{name: string, case: string, session: object, [error]: string}} Experiment
 * Experiment type returned from 'joinExperiment' function
 */

/**
 * Sets up a/b testing, using `abSessionId` cookie from the request,
 * if any.
 * It creates a sixpack session and sends the request to our sixpack api
 * to receive the a/b case selected for current user, and saves it to
 * the Vuex store `experiments` array.
 *
 * @param {string} serverCookie - Server cookie string from `req.headers`
 * @param {import('vuex).Commit} commit - Vuex commit
 * @returns {Promise<void>}
 */
const setupAbTesting = async (serverCookie, commit) => {
  const existingAbSessionId = getCookieValue(serverCookie, 'abSessionId')
  const session = createSixpackSession(existingAbSessionId)
  await setupExperiments(commit, session)
}

/**
 * Attach each a/b test (aka "experiment") to the sixpack session
 * and commit a vuex mutation for each joined experiment
 * @param {import('vuex').Commit} commit - Vuex commit
 * @param {object} session - Sixpack session object
 * @returns {Promise<void>}
 */
const setupExperiments = (commit, session) => {
  // List all active experiments here
  const experimentPromises = [donationLanguage(session)]
  return (
    Promise.all(experimentPromises)
      .then((experiments) =>
        experiments.map((experiment) =>
          commit(JOINED_AB_TEST_EXPERIMENT, {
            name: experiment.name,
            case: experiment.case,
            session: experiment.session,
          })
        )
      )
      // In the case of an error, the user joins the default version of an experiment
      .catch((error) =>
        commit(JOINED_AB_TEST_EXPERIMENT, {
          name: error.name,
          case: error.case,
          session: error.session,
        })
      )
  )
}

export { setupAbTesting, setupExperiments }
