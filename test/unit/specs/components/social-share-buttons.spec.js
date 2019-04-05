import SocialShareButtons from '@/components/SocialShareButtons';
import render from '../../test-utils/render';

describe('SocialShareButtons', () => {
  let options = null;
  let props = null;

  beforeEach(() => {
    props = {
      shareURL: 'http://share.url',
      imageURL: 'http://image.url',
      shareText: 'share text',
    };

    options = {
      propsData: props,
    };
  });

  it('should render all buttons with correct query params', () => {
    const wrapper = render(SocialShareButtons, options);
    expect(wrapper.find('.social-button.facebook').html()).toContain('?u=http://share.url&amp;t==share');
    expect(wrapper.find('.social-button.twitter').html()).toContain('?text=share text');
    expect(wrapper.find('.social-button.pinterest').html()).toContain('?media=http://image.url&amp;description=share text');
  });
});
