import NavSection from '@/components/NavSection';
import render from '../../test-utils/render';

describe('NavSection', () => {
  it('should render correct contents', () => {
    const wrapper = render(NavSection);
    expect(wrapper.find('nav').vm).toBeDefined();
  });
});
