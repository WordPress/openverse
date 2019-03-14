import PhotoDetails from '@/components/PhotoDetails';
import render from '../../test-utils/render';

describe('PhotoDetails', () => {
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

    process.env.API_URL = 'https://foo.bar';
  });

  it('should render correct contents', () => {
    const wrapper = render(PhotoDetails, options);
    expect(wrapper.find('.photo_image').element).toBeDefined();
    expect(wrapper.find({ name: 'license-icons' }).element).toBeDefined();
  });

  it('should render watermark link', () => {
    const wrapper = render(PhotoDetails, options);
    expect(wrapper.find('.download-watermark').element).toBeDefined();
  });

  it('should generate license URL', () => {
    const wrapper = render(PhotoDetails, options);
    expect(wrapper.vm.ccLicenseURL).toBe('https://creativecommons.org/licenses/BY/1.0');
  });

  it('should generate CC0 license URL', () => {
    options.propsData.image.license = 'cc0';
    const wrapper = render(PhotoDetails, options);
    expect(wrapper.vm.ccLicenseURL).toBe('https://creativecommons.org/publicdomain/zero/1.0/');
  });

  it('should generate CC PDM license URL', () => {
    options.propsData.image.license = 'pdm';
    const wrapper = render(PhotoDetails, options);
    expect(wrapper.vm.ccLicenseURL).toBe('https://creativecommons.org/publicdomain/mark/1.0/');
  });

  it('should generate license name', () => {
    const wrapper = render(PhotoDetails, options);
    expect(wrapper.vm.fullLicenseName).toBe('CC BY 1.0');
  });

  it('should generate CC-0 license name', () => {
    options.propsData.image.license = 'cc0';
    const wrapper = render(PhotoDetails, options);
    expect(wrapper.vm.fullLicenseName).toBe('cc0 1.0');
  });

  it('should generate watermark url', () => {
    const wrapper = render(PhotoDetails, options);
    expect(wrapper.vm.watermarkURL).toContain(`https://foo.bar/watermark/${props.image.id}`);
  });

  it('should generate watermark url with embed_metadata set to true', () => {
    const wrapper = render(PhotoDetails, options);
    wrapper.setData({ shouldEmbedMetadata: true });
    expect(wrapper.vm.watermarkURL).toContain('embed_metadata=true');
  });

  it('should generate watermark url with embed_metadata set to false', () => {
    const wrapper = render(PhotoDetails, options);
    wrapper.setData({ shouldEmbedMetadata: false });
    expect(wrapper.vm.watermarkURL).toContain('embed_metadata=false');
  });

  it('should generate watermark url with watermark set to true', () => {
    const wrapper = render(PhotoDetails, options);
    wrapper.setData({ shouldWatermark: true });
    expect(wrapper.vm.watermarkURL).toContain('watermark=true');
  });

  it('should generate watermark url with watermark set to false', () => {
    const wrapper = render(PhotoDetails, options);
    wrapper.setData({ shouldWatermark: false });
    expect(wrapper.vm.watermarkURL).toContain('watermark=false');
  });

  it('should generate text attribution', () => {
    const wrapper = render(PhotoDetails, options);
    expect(wrapper.vm.textAttribution()).toContain(props.image.title);
    expect(wrapper.vm.textAttribution()).toContain('is licensed under CC');
    expect(wrapper.vm.textAttribution()).toContain(props.image.license.toUpperCase());
    expect(wrapper.vm.textAttribution()).toContain(props.image.license_version);
    expect(wrapper.vm.textAttribution()).toContain(wrapper.vm.ccLicenseURL);
  });

  it('should generate html attribution', () => {
    const wrapper = render(PhotoDetails, options);
    expect(wrapper.vm.HTMLAttribution()).toContain(`<a href="${props.image.creator_url}">${props.image.creator}</a>`);
    expect(wrapper.vm.HTMLAttribution()).toContain(`<a href="${props.image.foreign_landing_url}">"${props.image.title}"</a>`);
    expect(wrapper.vm.HTMLAttribution()).toContain(`<a href="${wrapper.vm.ccLicenseURL}">`);
  });

  it('renders link back to search results if enabled', () => {
    const wrapper = render(PhotoDetails, {
      propsData: {
        ...props,
        shouldShowBreadcrumb: true,
      },
    });
    expect(wrapper.find('.photo_breadcrumb').element).toBeDefined();
  });

  it('doesnt render link back to search results if disabled', () => {
    const wrapper = render(PhotoDetails, {
      propsData: {
        ...props,
        shouldShowBreadcrumb: false,
      },
    });
    expect(wrapper.find('.photo_breadcrumb').element).toBeUndefined();
  });

  it('redirects back when clicking on the back to results link', () => {
    const routerMock = {
      push: jest.fn(),
    };
    const opts = {
      propsData: {
        ...props,
        shouldShowBreadcrumb: true,
        query: {
          q: 'foo',
        },
      },
      mocks: {
        $router: routerMock,
      },
    };
    const wrapper = render(PhotoDetails, opts);
    const link = wrapper.find('.photo_breadcrumb');
    link.trigger('click');
    expect(routerMock.push).toHaveBeenCalledWith({ name: 'browse-page', query: opts.propsData.query });
  });
});
