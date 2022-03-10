import VCopyLicense from '~/components/VMediaInfo/VCopyLicense.vue'

import render from '../../../test-utils/render'

describe('VCopyLicense', () => {
  let options = null
  let props = null

  beforeEach(() => {
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
    }
  })

  it('should contain the correct contents', () => {
    const wrapper = render(VCopyLicense, options)
    expect(wrapper.find('.copy-license')).toBeDefined()
  })
})
