import PhotoDetails from '@/components/PhotoDetails';
import render from '../../test-utils/render';

describe('PhotoDetails', () => {
  const props = {
    image: {
      id: 0,
      title: 'foo',
      provider: 'flickr',
      url: 'foo.bar',
      thumbnail: 'http://foo.bar',
      foreign_landing_url: 'http://foo.bar',
      license: 'CC-BY',
      license_version: '1.0',
      creator: 'John',
      creator_url: 'http://creator.com',
    },
  };
  const options = {
    propsData: props,
  };
  it('should render correct contents', () => {
    const wrapper = render(PhotoDetails, options);
    expect(wrapper.find('.photo_image').element).toBeDefined();
    expect(wrapper.find({ name: 'license-icons' }).element).toBeDefined();
  });

  it('should generate license URL', () => {
    const wrapper = render(PhotoDetails, options);
    expect(wrapper.vm.ccLicenseURL).toBe('https://creativecommons.org/licenses/CC-BY/1.0');
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
