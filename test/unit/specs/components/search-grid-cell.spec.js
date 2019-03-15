import SearchGridCell from '@/components/SearchGridCell';
import render from '../../test-utils/render';

describe('SearchGridCell', () => {
  it('should render correct contents', () => {
    const props = {
      image: {
        id: 0,
        title: 'foo',
        provider: 'flickr',
        url: 'foo.bar',
        thumbnail: 'foo.bar',
        foreign_landing_url: 'foo.bar',
      },
    };
    const wrapper = render(SearchGridCell, { propsData: props });
    expect(wrapper.find('div').find('figure').element).toBeDefined();
  });
});
