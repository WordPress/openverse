import LicenseIcons from '@/components/LicenseIcons';
import render from '../../test-utils/render';

describe('LicenseIcons', () => {
  let options = null;
  let props = null;
  let image = null;

  beforeEach(() => {
    image = {
      license: 'by',
      license_version: '1.0',
    };
    props = {
      image,
    };

    options = {
      propsData: props,
    };
  });

  it('should render correct contents', () => {
    const wrapper = render(LicenseIcons, options);
    expect(wrapper.find('.photo-license-icons').element).toBeDefined();
  });

  it('should generate CC BY icons', () => {
    const wrapper = render(LicenseIcons, options);
    expect(wrapper.find('.cc-logo').element).toBeDefined();
    expect(wrapper.find('.cc-by').element).toBeDefined();
  });

  it('should generate CC BY SA icons', () => {
    image.license = 'by-sa';
    const wrapper = render(LicenseIcons, options);
    expect(wrapper.find('.cc-logo').element).toBeDefined();
    expect(wrapper.find('.cc-by').element).toBeDefined();
    expect(wrapper.find('.cc-sa').element).toBeDefined();
  });

  it('should generate CC BY ND icons', () => {
    image.license = 'by-nd';
    const wrapper = render(LicenseIcons, options);
    expect(wrapper.find('.cc-logo').element).toBeDefined();
    expect(wrapper.find('.cc-by').element).toBeDefined();
    expect(wrapper.find('.cc-nd').element).toBeDefined();
  });

  it('should generate CC0 icons', () => {
    image.license = 'cc0';
    const wrapper = render(LicenseIcons, options);
    expect(wrapper.find('.cc-logo').element).toBeDefined();
    expect(wrapper.find('.cc-zero').element).toBeDefined();
  });

  it('should generate PDM icons', () => {
    image.license = 'pdm';
    const wrapper = render(LicenseIcons, options);
    expect(wrapper.find('.cc-logo').element).toBeDefined();
    expect(wrapper.find('.cc-pd').element).toBeDefined();
  });

  it('should generate license URL', () => {
    const wrapper = render(LicenseIcons, options);
    expect(wrapper.attributes('href')).toBe('https://creativecommons.org/licenses/by/1.0');
  });

  it('should generate license URL for cc0', () => {
    image.license = 'cc0';
    const wrapper = render(LicenseIcons, options);
    expect(wrapper.attributes('href')).toBe('https://creativecommons.org/publicdomain/zero/1.0/');
  });

  it('should generate license URL for PDM', () => {
    image.license = 'pdm';
    const wrapper = render(LicenseIcons, options);
    expect(wrapper.attributes('href')).toBe('https://creativecommons.org/publicdomain/mark/1.0/');
  });
});
