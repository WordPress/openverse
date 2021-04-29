import abTests from '~/abTests'
import { JOINED_AB_TEST_EXPERIMENT } from '~/store-modules/mutation-types'
import donationLanguage from '~/abTests/experiments/donationLanguage'

process.env.API_URL = 'http://api.cc.org/v1/'

describe('AB Tests', () => {
  let store = {}

  beforeEach(() => {
    store = {
      commit: jest.fn(),
      state: {
        sessionId: 'foo',
      },
    }
  })

  it('sets up experiments', (done) => {
    const result = abTests(store, [donationLanguage])
    result.then(() => {
      expect(store.commit.mock.calls[0][0]).toBe(JOINED_AB_TEST_EXPERIMENT)
      done()
    })
  })
})
