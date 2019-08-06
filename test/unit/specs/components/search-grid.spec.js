import SearchGrid from '@/components/SearchGridManualLoad';
import render from '../../test-utils/render';

describe('SearchGrid', () => {
  it('should render correct contents', () => {
    const wrapper = render(SearchGrid, {
      propsData: {
        query: { q: 'foo' },
      },
      mocks: {
        $store: {
          state: {
            imagesCount: 100,
          },
        },
      },
    });
    expect(wrapper.find('section').vm).toBeDefined();
  });
});
