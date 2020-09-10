import store from '~/store-modules/social-store'
import { SocialMediaShare } from '~/analytics/events'

describe('Social Media Store', () => {
  describe('actions', () => {
    let googleAnalyticsMock = null

    beforeEach(() => {
      googleAnalyticsMock = () => ({
        sendEvent: jest.fn(),
      })
    })

    it('SOCIAL_MEDIA_SHARE sends social media share event', () => {
      const data = {
        site: 'Facebook',
      }
      store.actions(googleAnalyticsMock).SOCIAL_MEDIA_SHARE({}, data)

      expect(googleAnalyticsMock().sendEvent).toHaveBeenCalledWith(
        new SocialMediaShare(data.site)
      )
    })
  })
})
