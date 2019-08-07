import SearchGrid from '@/components/SearchGridManualLoad';
import render from '../../test-utils/render';

describe('SearchGrid', () => {
  let options = {};

  beforeEach(() => {
    options = {
      propsData: {
        query: { q: 'foo' },
        includeAnalytics: true,
      },
      mocks: {
        $store: {
          state: {
            imagesCount: 100,
          },
        },
      },
    };
  });

  it('should render correct contents', () => {
    const wrapper = render(SearchGrid, options);
    expect(wrapper.find('section').element).toBeDefined();
    expect(wrapper.find('.load-more').element).toBeDefined();
  });

  it('doesnt render load more button if is loading images', () => {
    options.propsData.isFetchingImages = true;
    const wrapper = render(SearchGrid, options);
    expect(wrapper.find('.load-more').vm).not.toBeDefined();
  });
});
