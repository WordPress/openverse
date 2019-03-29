import Homepage from '@/pages/HomePage';
import { SET_QUERY } from '@/store/mutation-types';
import render from '../../test-utils/render';

describe('Homepage', () => {
  it('should render correct contents', () => {
    const wrapper = render(Homepage);

    expect(wrapper.find({ name: 'header-section' }).vm).toBeDefined();
    expect(wrapper.find({ name: 'footer-section' }).vm).toBeDefined();
    expect(wrapper.find({ name: 'license-icons' }).vm).toBeDefined();

  });

  it('should expose correct data values', () => {
    const wrapper = render(Homepage);

    expect(wrapper.vm.$data.images).toHaveLength(7);
  });

  it('commits a mutation when category is clicked', () => {
    const storeMock = {
      commit: jest.fn(),
    };
    const opts = {
      mocks: {
        $store: storeMock,
      },
    };
  
    const wrapper = render(Homepage, opts);
    const category = wrapper.find('.featured-images_banner').text().toLowerCase();
    wrapper.find('.featured-images_item').trigger('click');
    expect(storeMock.commit).toHaveBeenCalledWith(SET_QUERY, { query: { q: category }, shouldNavigate: true });
  });

  it('redirects to detail page when clicking on image in header-grid', () => {
    const routerMock = {
      push: jest.fn(),
    };
    const opts = {
      mocks: {
        $router: routerMock,
      },
    };
    const wrapper = render(Homepage, opts);
    wrapper.setData({ images: [ 
        { 
          class: 'grid-item block b1',
          id: '2b091d94'
        } 
      ] 
    });

    wrapper.find('.grid-item').trigger('click');;
    expect(routerMock.push).toHaveBeenCalledWith(`/photos/2b091d94`);
  });
});
