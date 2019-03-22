import RelatedImages from '@/components/RelatedImages';
import SearchGrid from '@/components/SearchGrid';
import render from '../../test-utils/render';

describe('RelatedImages', () => {
  it('should render correct contents', () => {
    const wrapper = render(RelatedImages);
    expect(wrapper.find({ name : 'related-images'}).element).toBeDefined();
    expect(wrapper.find('search-grid').exists()).toBe(false);
  });
});
