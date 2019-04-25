import CopyAttributionButtons from '@/components/CopyAttributionButtons';
import render from '../../test-utils/render';

describe('CopyAttributionButtons', () => {
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
      ccLicenseURL: 'http://licensefoo.bar',
      fullLicenseName: 'BY',
    };

    options = {
      propsData: props,
    };
  });

  it('should generate text attribution', () => {
    const wrapper = render(CopyAttributionButtons, options);
    expect(wrapper.vm.textAttribution()).toContain(props.image.title);
    expect(wrapper.vm.textAttribution()).toContain('is licensed under');
    expect(wrapper.vm.textAttribution()).toContain(props.fullLicenseName);
    expect(wrapper.vm.textAttribution()).toContain(props.ccLicenseURL);
  });

  it('should generate html attribution', () => {
    const wrapper = render(CopyAttributionButtons, options);
    expect(wrapper.vm.HTMLAttribution()).toContain(`<a href="${props.image.creator_url}">${props.image.creator}</a>`);
    expect(wrapper.vm.HTMLAttribution()).toContain(`<a href="${props.image.foreign_landing_url}">"${props.image.title}"</a>`);
    expect(wrapper.vm.HTMLAttribution()).toContain(`<a href="${props.ccLicenseURL}">`);
  });

  it('should generate html attribution without creator URL', () => {
    options.propsData.image.creator_url = null;
    const wrapper = render(CopyAttributionButtons, options);
    expect(wrapper.vm.HTMLAttribution()).toContain(`by ${props.image.creator}`);
    expect(wrapper.vm.HTMLAttribution()).toContain(`<a href="${props.image.foreign_landing_url}">"${props.image.title}"</a>`);
    expect(wrapper.vm.HTMLAttribution()).toContain(`<a href="${props.ccLicenseURL}">`);
  });

  it('should generate html attribution without creator URL', () => {
    options.propsData.image.creator = null;
    const wrapper = render(CopyAttributionButtons, options);
    expect(wrapper.vm.HTMLAttribution()).not.toContain('by');
    expect(wrapper.vm.HTMLAttribution()).toContain(`<a href="${props.image.foreign_landing_url}">"${props.image.title}"</a>`);
    expect(wrapper.vm.HTMLAttribution()).toContain(`<a href="${wrapper.vm.ccLicenseURL}">`);
  });
});
