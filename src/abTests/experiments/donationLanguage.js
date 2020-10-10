const EXPERIMENT_NAME = 'donation_language'
const DONATION_GENERAL_CASE = 'donation_general'
const DONATION_PERCENTAGE_CASE = 'donation_percentage'

/**
 * Joins the experiment.
 *
 * Returns a Promise, which resolves with the experiment name and selected experiment case.
 * In case of failure, it rejects with the error, the experiment name and a default experiment case
 * @param {*} session Sixpack session object
 * @returns {Promise<Experiment>}
 */
const joinExperiment = (session) => {
  const resultPromise = new Promise((resolve, reject) => {
    session.participate(
      EXPERIMENT_NAME,
      [DONATION_GENERAL_CASE, DONATION_PERCENTAGE_CASE],
      (err, res) => {
        if (err || res.error) {
          reject({
            error: err,
            name: EXPERIMENT_NAME,
            case: DONATION_GENERAL_CASE,
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
  DONATION_GENERAL_CASE,
  DONATION_PERCENTAGE_CASE,
}
