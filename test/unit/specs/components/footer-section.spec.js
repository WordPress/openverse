import FooterSection from '@/components/FooterSection';
import render from '../../test-utils/render';

describe('FooterSection', () => {
  it('should render correct contents', () => {
    const wrapper = render(FooterSection);
    expect(wrapper.find('footer').vm).toBeDefined();
  });
});
