import ShareList from '@/components/ShareList';
import render from '../../test-utils/render';

describe('ShareList', () => {

  it('should render correct contents', () => {
    const wrapper = render(ShareList);
    expect(wrapper.find({ name: 'share-list' }).element).toBeDefined();
  });
});
