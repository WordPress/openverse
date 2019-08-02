import { JOINED_AB_TEST_EXPERIMENT } from '@/store/mutation-types';
import createSixpackSession from './createSixpackSession';
import InfiniteLoadingExperiment from './infiniteLoadingExperiment';

const setupExperiments = (store) => {
  const session = createSixpackSession();

  const experimentPromises = [
    InfiniteLoadingExperiment(session),
  ];

  return Promise.all(experimentPromises).then(experiments => experiments.map(experiment =>
    store.commit(JOINED_AB_TEST_EXPERIMENT, {
      name: experiment.name,
      case: experiment.case,
    }),
  )).catch(error =>
    store.commit(JOINED_AB_TEST_EXPERIMENT, {
      name: error.name,
      case: error.case,
    }),
  );
};

export default setupExperiments;
