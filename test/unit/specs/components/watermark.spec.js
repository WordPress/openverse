import Watermark from '@/components/Watermark';
import render from '../../test-utils/render';

describe('Watermark', () => {
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
    };

    options = {
      propsData: props,
    };

    process.env.API_URL = 'https://watermark.test';
  });

  it('should render watermark link', () => {
    const wrapper = render(Watermark, options);
    expect(wrapper.find('.button').element).toBeDefined();
  });

  it('should generate watermark url', () => {
    const wrapper = render(Watermark, options);
    expect(wrapper.vm.watermarkURL).toContain(`https://watermark.test/watermark/${props.image.id}`);
  });

  it('should generate watermark url with embed_metadata set to true', () => {
    const wrapper = render(Watermark, options);
    wrapper.setData({ shouldEmbedMetadata: true });
    expect(wrapper.vm.watermarkURL).toContain('embed_metadata=true');
  });

  it('should generate watermark url with embed_metadata set to false', () => {
    const wrapper = render(Watermark, options);
    wrapper.setData({ shouldEmbedMetadata: false });
    expect(wrapper.vm.watermarkURL).toContain('embed_metadata=false');
  });

  it('should generate watermark url with watermark set to true', () => {
    const wrapper = render(Watermark, options);
    wrapper.setData({ shouldWatermark: true });
    expect(wrapper.vm.watermarkURL).toContain('watermark=true');
  });

  it('should generate watermark url with watermark set to false', () => {
    const wrapper = render(Watermark, options);
    wrapper.setData({ shouldWatermark: false });
    expect(wrapper.vm.watermarkURL).toContain('watermark=false');
  });

  it('should dispatch to the store when button is clicked', () => {
    const storeMock = {
      dispatch: jest.fn(),
    };
    const wrapper = render(Watermark, { ...options, mocks: { $store: storeMock } });
    wrapper.find('.button').trigger('click');
    expect(storeMock.dispatch).toHaveBeenCalledWith('DOWNLOAD_WATERMARK', {
      imageId: props.image.id,
      shouldWatermark: wrapper.vm.shouldWatermark,
      shouldEmbedMetadata: wrapper.vm.shouldEmbedMetadata,
    });
  });
});
