import BugReport from '@/components/BugReport';
import render from '../../test-utils/render';

describe('BugReport', () => {
  let options = {};
  let dispatchMock = null;
  beforeEach(() => {
    dispatchMock = jest.fn();
    options = {
      mocks: {
        $store: {
          dispatch: dispatchMock,
        },
      },
    };
  });

  it('should render correct contents', () => {
    const wrapper = render(BugReport, options);
    expect(wrapper.find('.bug-report').vm).toBeDefined();
  });

  it('should not render required field notice by default', () => {
    const wrapper = render(BugReport, options);
    expect(wrapper.find('.error-message').vm).toBeUndefined();
  });

  it('should render required field notice when fields are empty', () => {
    const wrapper = render(BugReport, options);
    const button = wrapper.find('.submit-form');
    button.trigger('click');
    expect(wrapper.findAll('.error-message').length).toBeGreaterThan(0);
  });
});
