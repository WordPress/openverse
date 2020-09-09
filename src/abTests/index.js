import { JOINED_AB_TEST_EXPERIMENT } from '~/store-modules/mutation-types'
import createSixpackSession from './lib/createSixpackSession'
import filterExpansion from './experiments/filterExpansion'

/**
 * Attach each a/b test (aka "experiment") to the sixpack session
 * and commit a vuex mutation for each joined experiment
 */
const setupExperiments = (store) => {
  const session = createSixpackSession(store.state.sessionId)
  // List all active experiments here
  const experimentPromises = [filterExpansion(session)]

  return (
    Promise.all(experimentPromises)
      .then((experiments) =>
        experiments.map((experiment) =>
          store.commit(JOINED_AB_TEST_EXPERIMENT, {
            name: experiment.name,
            case: experiment.case,
            session: experiment.session,
          })
        )
      )
      // In the case of an error, the user joins the default version of an experiment
      .catch((error) =>
        store.commit(JOINED_AB_TEST_EXPERIMENT, {
          name: error.name,
          case: error.case,
          session: error.session,
        })
      )
  )
}

export default setupExperiments
