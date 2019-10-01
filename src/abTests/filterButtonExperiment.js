const EXPERIMENT_NAME = 'filter_experiment';
const ORIGINAL_FILTER_BUTTON_EXPERIMENT = 'original_filter_button_experiment';
const FILTER_BUTTON_NEW_POSITION_EXPERIMENT = 'filter_button_new_position_experiment';

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
      [ORIGINAL_FILTER_BUTTON_EXPERIMENT, FILTER_BUTTON_NEW_POSITION_EXPERIMENT],
      (err, res) => {
        if (err || res.error) {
          reject({
            error: err,
            name: EXPERIMENT_NAME,
            case: ORIGINAL_FILTER_BUTTON_EXPERIMENT,
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
  ORIGINAL_FILTER_BUTTON_EXPERIMENT,
  FILTER_BUTTON_NEW_POSITION_EXPERIMENT,
};
