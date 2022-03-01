import { mount } from '@vue/test-utils'

import {
  DETAIL_PAGE_EVENTS,
  SEND_DETAIL_PAGE_EVENT,
} from '~/constants/usage-data-analytics-types'
import { USAGE_DATA } from '~/constants/store-modules'

import ReuseSurvey from '~/components/ImageDetails/ReuseSurvey'

import i18n from '../../../test-utils/i18n'
import render from '../../../test-utils/render'

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
    const wrapper = render(ReuseSurvey, options, mount)
    wrapper.find('a').trigger('click')
    expect(dispatchMock).toHaveBeenCalledWith(
      `${USAGE_DATA}/${SEND_DETAIL_PAGE_EVENT}`,
      {
        eventType: DETAIL_PAGE_EVENTS.REUSE_SURVEY,
        resultUuid: props.image.id,
      }
    )
  })
})
