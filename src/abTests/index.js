import { JOINED_AB_TEST_EXPERIMENT } from '@/store/mutation-types'
import createSixpackSession from './createSixpackSession'
import filterVisibilityExperiment from './filterVisibilityExperiment'

const setupExperiments = (store) => {
  const session = createSixpackSession(store.state.sessionId)

  const experimentPromises = [filterVisibilityExperiment(session)]

  return Promise.all(experimentPromises)
    .then((experiments) =>
      experiments.map((experiment) =>
        store.commit(JOINED_AB_TEST_EXPERIMENT, {
          name: experiment.name,
          case: experiment.case,
          session: experiment.session,
        })
      )
    )
    .catch((error) =>
      store.commit(JOINED_AB_TEST_EXPERIMENT, {
        name: error.name,
        case: error.case,
        session: error.session,
      })
    )
}

export default setupExperiments
