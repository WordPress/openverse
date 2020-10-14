import ReuseSurvey from '~/components/ImageDetails/ReuseSurvey'
import {
  DETAIL_PAGE_EVENTS,
  SEND_DETAIL_PAGE_EVENT,
} from '~/store-modules/usage-data-analytics-types'
import render from '../../../test-utils/render'
import i18n from '../../../test-utils/i18n'

describe('ImageAttribution', () => {
  let options = null
  let props = null
  let dispatchMock = null
  const $t = (key) => i18n.messages[key]
  beforeEach(() => {
    dispatchMock = jest.fn()
    props = {
      image: {
        id: 0,
      },
    }
    options = {
      propsData: props,
      mocks: {
        $store: {
          dispatch: dispatchMock,
        },
        $t,
      },
    }
  })

  it('should dispatch REUSE_SURVEY on reuse link clicked', () => {
    const wrapper = render(ReuseSurvey, options)
    wrapper.find('a').trigger('click')
    expect(dispatchMock).toHaveBeenCalledWith(SEND_DETAIL_PAGE_EVENT, {
      eventType: DETAIL_PAGE_EVENTS.REUSE_SURVEY,
      resultUuid: props.image.id,
    })
  })
})
