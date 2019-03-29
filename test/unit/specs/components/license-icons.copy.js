import LicenseIcons from '@/components/LicenseIcons';
import render from '../../test-utils/render';

describe('LicenseIcons', () => {
  let options = null;
  let props = null;
  
  beforeEach(() => {
    props = {
      image: {
        license: 'BY',
        license_version: '1.0',
      }
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
    expect(wrapper.findAll('.photo-license-icon').at(0)).toBeDefined();
    expect(wrapper.findAll('.photo-license-icon').at(1)).toBeDefined();
  });

  it('should generate license URL', () => {
    const wrapper = render(LicenseIcons, options);
    expect(wrapper.attributes('href')).toBe('https://creativecommons.org/licenses/BY/1.0');
  });
});
