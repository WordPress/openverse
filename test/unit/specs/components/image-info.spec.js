import ImageInfo from '@/components/ImageInfo';
import render from '../../test-utils/render';

describe('Image Info', () => {
  let props = null;
  let options = {};
  let storeState = null;
  let commitMock = null;

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
      imageHeight: 1000,
      imageWidth: 500,
    };

    commitMock = jest.fn();

    storeState = {
      $store: {
        commit: commitMock,
        state: {
          isReportFormVisible: false,
        },
      },
    };

    options = {
      propsData: props,
      mocks: {
        ...storeState,
      },
    };
  });

  it('should contain the corect contents', () => {
    const wrapper = render(ImageInfo, options);
    expect(wrapper.find('.sidebar_section').element).toBeDefined();
  });

  it('should contain correct information', () => {
    const wrapper = render(ImageInfo, options);
    expect(wrapper.html()).toContain(props.image.title);
    expect(wrapper.find('.photo_license').text()).toBe(props.fullLicenseName);
  });

  it('should contain display not available if there is no image creator', () => {
    props.image.creator = null;
    const wrapper = render(ImageInfo, options);
    expect(wrapper.html()).toContain('Not Available');
  });

  it('should display image dimensions', () => {
    const wrapper = render(ImageInfo, options);
    expect(wrapper.html()).toContain(`${props.imageWidth}`);
    expect(wrapper.html()).toContain(`${props.imageHeight} pixels`);
  });

  it('should toggle visibility of report form on report button click', () => {
    const wrapper = render(ImageInfo, options);
    const button = wrapper.find('.report');
    button.trigger('click');

    expect(commitMock).toHaveBeenCalledWith('TOGGLE_REPORT_FORM_VISIBILITY');
  });

  it(' report form should be invisible by default', () => {
    const wrapper = render(ImageInfo, options);

    expect(wrapper.find({ name: 'content-report-form' }).vm).not.toBeDefined();
  });

  it(' report form should be visible when isReportFormVisible is true', () => {
    storeState.$store.state.isReportFormVisible = true;
    const wrapper = render(ImageInfo, options);

    expect(wrapper.find({ name: 'content-report-form' }).vm).toBeDefined();
  });
});
