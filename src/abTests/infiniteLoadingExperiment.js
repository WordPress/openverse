const EXPERIMENT_NAME = 'infinite_loading_experiment';
const EXPERIMENT_CASE_ONE = 'infinite_loading';
const EXPERIMENT_CASE_TWO = 'manual_loading';

/**
 * Joins the experiment.
 *
 * Returns a Promise, which resolves with the experiment name and selected experiment case.
 * In case of failure, it rejects with the error, the experiment name and a default experiment case
 * @param {*} session Sixpack session object
 */
const joinExperiment = (session) => {
  const resultPromise = new Promise((resolve, reject) => {
    session.participate(EXPERIMENT_NAME, [EXPERIMENT_CASE_ONE, EXPERIMENT_CASE_TWO], (err, res) => {
      if (err || res.error) {
        reject({
          error: err,
          name: EXPERIMENT_NAME,
          case: EXPERIMENT_CASE_ONE,
        });
      }

      const experimentCase = res.alternative.name;

      resolve({
        name: EXPERIMENT_NAME,
        case: experimentCase,
      });
    });
  });

  return resultPromise;
};

export default joinExperiment;
export const ExperimentData = {
  EXPERIMENT_NAME,
  EXPERIMENT_CASE_ONE,
  EXPERIMENT_CASE_TWO,
};
