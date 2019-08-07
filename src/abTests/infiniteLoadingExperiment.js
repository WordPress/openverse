const EXPERIMENT_NAME = 'infinite_loading_experiment';
const INFINITE_LOADING_EXPERIMENT = 'infinite_loading';
const MANUAL_LOADING_EXPERIMENT = 'manual_loading';

/**
 * Joins the experiment.
 *
 * Returns a Promise, which resolves with the experiment name and selected experiment case.
 * In case of failure, it rejects with the error, the experiment name and a default experiment case
 * @param {*} session Sixpack session object
 */
const joinExperiment = (session) => {
  const resultPromise = new Promise((resolve, reject) => {
    session.participate(EXPERIMENT_NAME,
      [INFINITE_LOADING_EXPERIMENT, MANUAL_LOADING_EXPERIMENT],
      (err, res) => {
        if (err || res.error) {
          reject({
            error: err,
            name: EXPERIMENT_NAME,
            case: INFINITE_LOADING_EXPERIMENT,
            session,
          });
        }

        const experimentCase = res.alternative.name;

        resolve({
          name: EXPERIMENT_NAME,
          case: experimentCase,
          session,
        });
      });
  });

  return resultPromise;
};

export default joinExperiment;
export const ExperimentData = {
  EXPERIMENT_NAME,
  INFINITE_LOADING_EXPERIMENT,
  MANUAL_LOADING_EXPERIMENT,
};
