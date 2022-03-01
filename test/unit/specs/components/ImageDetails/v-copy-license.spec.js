import {
  DETAIL_PAGE_EVENTS,
  SEND_DETAIL_PAGE_EVENT,
} from '~/constants/usage-data-analytics-types'
import { USAGE_DATA } from '~/constants/store-modules'

import VCopyLicense from '~/components/VMediaInfo/VCopyLicense.vue'

import render from '../../../test-utils/render'

describe('VCopyLicense', () => {
  let options = null
  let props = null
  let dispatchMock = null

  const copyData = {
    type: 'Bar',
    event: {
      content: 'Foo',
    },
  }

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
        license_url: 'http://license.com',
        creator: 'John',
        creator_url: 'http://creator.com',
      },
      fullLicenseName: 'LICENSE',
    }
    options = {
      propsData: props,
      mocks: {
        $nuxt: {
          context: {
            store: {
              dispatch: dispatchMock,
            },
          },
        },
      },
    }
  })

  it('should contain the correct contents', () => {
    const wrapper = render(VCopyLicense, options)
    expect(wrapper.find('.copy-license')).toBeDefined()
  })

  it('should dispatch SEND_DETAIL_PAGE_EVENT on copy attribution', () => {
    const wrapper = render(VCopyLicense, options)
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
