import HomeLicenseFilter from '@/components/HomeLicenseFilter';
import render from '../../test-utils/render';

describe('HomeLicenseFilter', () => {
  let options = {};
  let commitMock = null;
  beforeEach(() => {
    commitMock = jest.fn();
    options = {
      mocks: {
        $store: {
          commit: commitMock,
        },
      },
    };
  });

  it('renders checkboxes', () => {
    const wrapper = render(HomeLicenseFilter, options);
    expect(wrapper.find('#commercial').element).toBeDefined();
    expect(wrapper.find('#modification').element).toBeDefined();
  });

  it('renders checkboxes', () => {
    const wrapper = render(HomeLicenseFilter, options);
    const commercialChk = wrapper.find('#commercial');
    const modificationChk = wrapper.find('#modification');

    commercialChk.trigger('click');
    modificationChk.trigger('click');

    expect(commitMock).toHaveBeenCalledWith('SET_QUERY', {
      query: {
        lt: 'commercial,modification',
      },
    });
  });
});
