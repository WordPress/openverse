import Homepage from '@/pages/HomePage';
import render from '../../test-utils/render';

describe('Homepage', () => {
  it('should render correct contents', () => {
    const wrapper = render(Homepage);

    expect(wrapper.find({ name: 'header-section' }).vm).toBeDefined();
    expect(wrapper.find({ name: 'hero-section' }).vm).toBeDefined();
    expect(wrapper.find({ name: 'footer-section' }).vm).toBeDefined();
  });
});
