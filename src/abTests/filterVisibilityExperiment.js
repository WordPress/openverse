const EXPERIMENT_NAME = 'filter_visibility_experiment'
const FILTERS_EXPANDED_EXPERIMENT = 'filters_expanded_experiment'
const FILTERS_COLLAPSED_EXPERIMENT = 'filters_collapsed_experiment'

/**
 * Joins the experiment.
 *
 * Returns a Promise, which resolves with the experiment name and selected experiment case.
 * In case of failure, it rejects with the error, the experiment name and a default experiment case
 * @param {*} session Sixpack session object
 */
const joinExperiment = (session) => {
  const resultPromise = new Promise((resolve, reject) => {
    session.participate(
      EXPERIMENT_NAME,
      [FILTERS_EXPANDED_EXPERIMENT, FILTERS_COLLAPSED_EXPERIMENT],
      (err, res) => {
        if (err || res.error) {
          reject({
            error: err,
            name: EXPERIMENT_NAME,
            case: FILTERS_COLLAPSED_EXPERIMENT,
            session,
          })
        }

        const experimentCase = res.alternative.name

        resolve({
          name: EXPERIMENT_NAME,
          case: experimentCase,
          session,
        })
      }
    )
  })

  return resultPromise
}

export default joinExperiment
export const ExperimentData = {
  EXPERIMENT_NAME,
  FILTERS_EXPANDED_EXPERIMENT,
  FILTERS_COLLAPSED_EXPERIMENT,
}
