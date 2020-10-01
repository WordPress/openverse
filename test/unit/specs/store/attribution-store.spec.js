import store from '~/store-modules/attribution-store'
import { CopyAttribution } from '~/analytics/events'

describe('Attribution Store', () => {
  describe('actions', () => {
    let gaInstance = null
    let googleAnalyticsMock = null

    beforeEach(() => {
      gaInstance = { sendEvent: jest.fn() }
      googleAnalyticsMock = jest.fn(() => gaInstance)
    })

    it('COPY_ATTRIBUTION sends copy event', () => {
      const data = {
        type: 'HTML Whatever',
        content: '<div>foo</div>',
      }
      store.actions(googleAnalyticsMock).COPY_ATTRIBUTION({}, data)

      expect(googleAnalyticsMock().sendEvent).toHaveBeenCalledWith(
        new CopyAttribution(data.type, data.content)
      )
    })
  })
})
