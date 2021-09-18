import SocialShareButtons from '~/components/ImageDetails/SocialShareButtons'
import { SOCIAL_MEDIA_SHARE } from '~/constants/action-types'
import {
  SEND_DETAIL_PAGE_EVENT,
  DETAIL_PAGE_EVENTS,
} from '~/store-modules/usage-data-analytics-types'
import render from '../../../test-utils/render'
import i18n from '../../../test-utils/i18n'

describe('SocialShareButtons', () => {
  let options = null
  let props = null
  let storeMock = null
  const $t = (key) => i18n.messages[key]

  beforeEach(() => {
    props = {
      image: {
        id: 0,
      },
      shareURL: 'http://share.url',
      imageURL: 'http://image.url',
      shareText: 'share text',
    }

    storeMock = {
      dispatch: jest.fn(),
    }

    options = {
      propsData: props,
      mocks: {
        $store: storeMock,
        $t,
      },
    }
  })

  it('should render all buttons with correct query params', () => {
    const wrapper = render(SocialShareButtons, options)
    expect(wrapper.find('.social-button.facebook').html()).toContain(
      '?u=http://share.url&amp;description=share'
    )
    expect(wrapper.find('.social-button.twitter').html()).toContain(
      '?text=share text'
    )
    expect(wrapper.find('.social-button.pinterest').html()).toContain(
      '?media=http://image.url&amp;description=share text'
    )
  })

  it('dispatches social media share event when facebook link is clicked', () => {
    const wrapper = render(SocialShareButtons, options)
    wrapper.find('.facebook').trigger('click')
    expect(storeMock.dispatch).toHaveBeenCalledWith(SOCIAL_MEDIA_SHARE, {
      site: 'Facebook',
    })

    expect(storeMock.dispatch).toHaveBeenCalledWith(SEND_DETAIL_PAGE_EVENT, {
      eventType: DETAIL_PAGE_EVENTS.SHARED_SOCIAL,
      resultUuid: props.image.id,
    })
  })

  it('dispatches social media share event when Twitter link is clicked', () => {
    const wrapper = render(SocialShareButtons, options)
    wrapper.find('.twitter').trigger('click')
    expect(storeMock.dispatch).toHaveBeenCalledWith(SOCIAL_MEDIA_SHARE, {
      site: 'Twitter',
    })

    expect(storeMock.dispatch).toHaveBeenCalledWith(SEND_DETAIL_PAGE_EVENT, {
      eventType: DETAIL_PAGE_EVENTS.SHARED_SOCIAL,
      resultUuid: props.image.id,
    })
  })

  it('dispatches social media share event when pinterest link is clicked', () => {
    const wrapper = render(SocialShareButtons, options)
    wrapper.find('.pinterest').trigger('click')
    expect(storeMock.dispatch).toHaveBeenCalledWith(SOCIAL_MEDIA_SHARE, {
      site: 'Pinterest',
    })

    expect(storeMock.dispatch).toHaveBeenCalledWith(SEND_DETAIL_PAGE_EVENT, {
      eventType: DETAIL_PAGE_EVENTS.SHARED_SOCIAL,
      resultUuid: props.image.id,
    })
  })
})
