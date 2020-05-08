import ImageAttribution from '@/components/ImageDetails/ImageAttribution';
import render from '../../test-utils/render';

describe('ImageAttribution', () => {
  let options = null;
  let props = null;

  beforeEach(() => {
    props = {
      image: {
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
    };
    options = {
      propsData: props,
    };
  });

  it('should contain the correct contents', () => {
    const wrapper = render(ImageAttribution, options);
    expect(wrapper.find('.sidebar_section')).toBeDefined();
  });

  it('should return the correct license url', () => {
    const wrapper = render(ImageAttribution, options);
    const a = wrapper.find('.photo_license');
    expect(a.attributes().href).toBe('http://license.com&atype=rich');
  });
});
