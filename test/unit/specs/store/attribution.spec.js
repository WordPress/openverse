import { createActions } from '~/store/attribution'
import { CopyAttribution } from '~/analytics/events'
import { COPY_ATTRIBUTION } from '~/constants/action-types'

describe('Attribution Store', () => {
  describe('actions', () => {
    let gaInstance = null
    let googleAnalyticsMock = null
    let actions = null

    beforeEach(() => {
      gaInstance = { sendEvent: jest.fn() }
      googleAnalyticsMock = jest.fn(() => gaInstance)
      actions = createActions(googleAnalyticsMock)
    })

    it('COPY_ATTRIBUTION sends copy event', () => {
      const data = {
        type: 'HTML Whatever',
        content: '<div>foo</div>',
      }
      actions[COPY_ATTRIBUTION]({}, data)

      expect(googleAnalyticsMock().sendEvent).toHaveBeenCalledWith(
        new CopyAttribution(data.type, data.content)
      )
    })
  })
})
