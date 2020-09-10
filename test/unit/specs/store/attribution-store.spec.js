import store from '~/store-modules/attribution-store'
import { CopyAttribution, EmbedAttribution } from '~/analytics/events'

describe('Attribution Store', () => {
  describe('actions', () => {
    let googleAnalyticsMock = null

    beforeEach(() => {
      googleAnalyticsMock = () => ({
        sendEvent: jest.fn(),
      })
    })

    it('COPY_ATTRIBUTION sends copy event', () => {
      const data = {
        content: '<div>foo</div>',
      }
      store.actions(googleAnalyticsMock).COPY_ATTRIBUTION({}, data)

      expect(googleAnalyticsMock.sendEvent).toHaveBeenCalledWith(
        new CopyAttribution(data.content)
      )
    })

    it('EMBED_ATTRIBUTION sends text event', () => {
      store.actions(googleAnalyticsMock).EMBED_ATTRIBUTION()

      expect(googleAnalyticsMock.sendEvent).toHaveBeenCalledWith(
        new EmbedAttribution()
      )
    })
  })
})
