import ShareList from '@/components/ShareList';
import render from '../../test-utils/render';

describe('ShareList', () => {

  it('should render correct contents', () => {
    const wrapper = render(ShareList);
   // expect(wrapper.vm).toBeDefined();
   expect(wrapper.find({ name: 'share-list' }).element).toBeDefined();
   expect(wrapper.find('.share-list_close-btn-ctr').element).toBeDefined();
  });
});
