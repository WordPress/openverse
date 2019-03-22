import SocialShareButtons from '@/components/SocialShareButtons';
import render from '../../test-utils/render';

describe('SocialShareButtons', () => {
  it('should render correct contents', () => {
    const wrapper = render(SocialShareButtons);
    expect(wrapper.find('.share-list_social-items').element).toBeDefined();
    expect(wrapper.find({ name: 'social-share-list' }).element).toBeDefined();
  });
});
