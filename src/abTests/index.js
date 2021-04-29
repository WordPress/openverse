import { JOINED_AB_TEST_EXPERIMENT } from '~/store-modules/mutation-types'
import { participate } from '~/utils/sixpack'

export const activeExperiments = []

/**
 * Attach each a/b test (aka "experiment") to the sixpack session
 * and commit a vuex mutation for each joined experiment.
 *
 * Each experiment is a simple object with the following structure:
 *
 * ```js
 * {
 *   name: 'experiment_name',
 *   defaultCase: 'experiment_default_case_name',
 *   cases: [
 *     'experiment_default_case_name',
 *     'any_other_case_names',
 *     'any_other_case_names',
 *   ],
 *   traffic_fraction: .10 // an optional number between 0 and 1 (100%)
 * }
 * Create a new file with the experiment object, import it here, and add it
 * to the active experiments array above.
 * ```
 */
const abTests = async (store, activeExperiments) => {
  // commit each experiment to Vuex
  const commitExperiments = (experiments) => {
    experiments.map((experiment) => {
      store.commit(JOINED_AB_TEST_EXPERIMENT, {
        name: experiment.name,
        case: experiment.case,
        session: experiment.session,
      })
    })
  }
  const experiments = await Promise.all(
    activeExperiments.map((experiment) =>
      participate(experiment, { sessionId: store.state.abSessionId })
    )
  )
  commitExperiments(experiments)
}

export default abTests
