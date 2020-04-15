import AboutPage from '@/pages/AboutPage';
import render from '../../test-utils/render';

describe('AboutPage', () => {
  it('should render correct contents', () => {
    const wrapper = render(AboutPage);

    expect(wrapper.find({ name: 'header-section' }).vm).toBeDefined();
    expect(wrapper.find({ name: 'footer-section' }).vm).toBeDefined();
    expect(wrapper.find('.table').element).toBeDefined();
  });
});
