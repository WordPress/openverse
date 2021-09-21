import CopyLicense from '~/components/MediaInfo/CopyLicense'
import { COPY_ATTRIBUTION } from '~/constants/action-types'
import {
  DETAIL_PAGE_EVENTS,
  SEND_DETAIL_PAGE_EVENT,
} from '~/constants/usage-data-analytics-types'

import render from '../../../test-utils/render'
import i18n from '../../../test-utils/i18n'
import { ATTRIBUTION, USAGE_DATA } from '~/constants/store-modules'

describe('CopyLicense', () => {
  let options = null
  let props = null
  const $t = (key) => i18n.messages[key]
  const copyData = {
    type: 'Bar',
    event: {
      content: 'Foo',
    },
  }

  let dispatchMock = null

  beforeEach(() => {
    dispatchMock = jest.fn()
    props = {
      media: {
        id: 0,
        title: 'foo',
        provider: 'flickr',
        url: 'foo.bar',
        thumbnail: 'http://foo.bar',
        foreign_landing_url: 'http://foo.bar',
        license: 'BY',
        license_version: '1.0',
        creator: 'John',
        creator_url: 'http://creator.com',
      },
      ccLicenseURL: 'http://license.com',
      fullLicenseName: 'LICENSE',
      attributionHtml: '<div>attribution</div>',
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

  it('should contain the correct contents', () => {
    const wrapper = render(CopyLicense, options)
    expect(wrapper.find('.copy-license')).toBeDefined()
  })

  it('should dispatch COPY_ATTRIBUTION', () => {
    const wrapper = render(CopyLicense, options)
    wrapper.vm.onCopyAttribution(copyData.type, copyData.event)
    expect(dispatchMock).toHaveBeenCalledWith(
      `${ATTRIBUTION}/${COPY_ATTRIBUTION}`,
      {
        type: copyData.type,
        content: copyData.event.content,
      }
    )
  })

  it('should dispatch SEND_DETAIL_PAGE_EVENT on copy attribution', () => {
    const wrapper = render(CopyLicense, options)
    wrapper.vm.onCopyAttribution(copyData.type, copyData.event)
    expect(dispatchMock).toHaveBeenCalledWith(
      `${USAGE_DATA}/${SEND_DETAIL_PAGE_EVENT}`,
      {
        eventType: DETAIL_PAGE_EVENTS.ATTRIBUTION_CLICKED,
        resultUuid: props.media.id,
      }
    )
  })
})
