import joinExperiment, {
  ExperimentData,
} from '~/abTests/experiments/filterExpansion'

describe('Infinite Loading Experiment', () => {
  let session = {}

  beforeEach(() => {
    session = {
      participate: jest
        .fn()
        .mockImplementation((name, alternatives, callback) =>
          callback(null, {
            alternative: {
              name: ExperimentData.FILTERS_COLLAPSED_CASE,
            },
          })
        ),
    }
  })

  it('joins experiment', (done) => {
    const result = joinExperiment(session)
    result.then((res) => {
      expect(res.name).toBe(ExperimentData.EXPERIMENT_NAME)
      expect(res.case).toBe(ExperimentData.FILTERS_COLLAPSED_CASE)
      expect(res.session).toBe(session)
      done()
    })
  })

  it('fails gracefully joining experiment', (done) => {
    session = {
      participate: jest
        .fn()
        .mockImplementation((name, alternatives, callback) =>
          callback({ error: 'foo' }, null)
        ),
    }
    const result = joinExperiment(session)
    result.catch((res) => {
      expect(res.name).toBe(ExperimentData.EXPERIMENT_NAME)
      expect(res.case).toBe(ExperimentData.FILTERS_COLLAPSED_CASE)
      expect(res.session).toBe(session)
      done()
    })
  })
})
