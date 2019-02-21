import SearchGrid from '@/components/SearchGrid';
import render from '../../test-utils/render';

describe('SearchGrid', () => {
  it('should render correct contents', () => {
    const wrapper = render(SearchGrid);
    expect(wrapper.find('section').vm).toBeDefined();
  });
});
