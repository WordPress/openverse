import SearchGridForm from '@/components/SearchGridFormNewFilter';
import render from '../../test-utils/render';

describe('SearchGridForm', () => {
  it('should render correct contents', () => {
    const wrapper = render(SearchGridForm);
    expect(wrapper.find('form').vm).toBeDefined();
  });
});
