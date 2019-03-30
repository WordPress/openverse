import SearchGridFilter from '@/components/SearchGridFilter';
import render from '../../test-utils/render';

describe('SearchGridFilter', () => {
  it('should render correct contents', () => {
    const wrapper = render(SearchGridFilter);
    expect(wrapper.find({ name: 'search-grid-filter' }).element).toBeDefined();
  });
});