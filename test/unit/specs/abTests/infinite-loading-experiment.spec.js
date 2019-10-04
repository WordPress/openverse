import joinExperiment, { ExperimentData } from '@/abTests/filterButtonExperiment';

describe('Infinite Loading Experiment', () => {
  let session = {};

  beforeEach(() => {
    session = {
      participate: jest.fn().mockImplementation((name, alternatives, callback) =>
        callback(null, {
          alternative: {
            name: ExperimentData.FILTER_BUTTON_NEW_POSITION_EXPERIMENT,
          },
        })),
    };
  });

  it('joins experiment', (done) => {
    const result = joinExperiment(session);
    result.then((res) => {
      expect(res.name).toBe(ExperimentData.EXPERIMENT_NAME);
      expect(res.case).toBe(ExperimentData.FILTER_BUTTON_NEW_POSITION_EXPERIMENT);
      expect(res.session).toBe(session);
      done();
    });
  });

  it('fails gracefully joining experiment', (done) => {
    session = {
      participate: jest.fn().mockImplementation((name, alternatives, callback) =>
        callback({ error: 'foo' }, null)),
    };
    const result = joinExperiment(session);
    result.catch((res) => {
      expect(res.name).toBe(ExperimentData.EXPERIMENT_NAME);
      expect(res.case).toBe(ExperimentData.ORIGINAL_FILTER_BUTTON_EXPERIMENT);
      expect(res.session).toBe(session);
      done();
    });
  });
});
