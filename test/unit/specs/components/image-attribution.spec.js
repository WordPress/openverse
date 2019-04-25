import ImageAttribution from '@/components/ImageAttribution';
import { COPY_ATTRIBUTION, EMBED_ATTRIBUTION } from '@/store/action-types';
import render from '../../test-utils/render';

describe('ImageAttribution', () => {
  let options = null;
  let props = null;
  const eventData = {
    content: 'Foo',
  };
  let dispatchMock = null;

  beforeEach(() => {
    dispatchMock = jest.fn();
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
      mocks: {
        $store: {
          dispatch: dispatchMock,
        },
      },
    };
  });

  it('should dispatch COPY_ATTRIBUTION', () => {
    const wrapper = render(ImageAttribution, options);
    wrapper.vm.onCopyAttribution(eventData);
    expect(dispatchMock).toHaveBeenCalledWith(COPY_ATTRIBUTION, {
      content: eventData.content,
    });
  });

  it('should dispatch EMBED_ATTRIBUTION', () => {
    const wrapper = render(ImageAttribution, options);
    wrapper.vm.onEmbedAttribution();
    expect(dispatchMock).toHaveBeenCalledWith(EMBED_ATTRIBUTION);
  });
});
