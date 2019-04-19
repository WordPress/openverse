import CopyButton from '@/components/CopyButton';
import { COPY_ATTRIBUTION } from '@/store/action-types';
import render from '../../test-utils/render';

describe('CopyButton', () => {
  let options = null;
  let props = null;
  const eventData = {
    text: 'Foo',
    clearSelection: jest.fn(),
  };
  let dispatchMock = null;

  beforeEach(() => {
    dispatchMock = jest.fn();
    props = {
      el: '#foo',
    };
    options = {
      propsData: props,
      mocks: {
        $store: {
          dispatch: dispatchMock,
        },
      },
    };
  });

  it('should render correct contents', () => {
    const wrapper = render(CopyButton, options);
    expect(wrapper.find('button').vm).toBeDefined();
  });

  it('data.success should be false by default', () => {
    const wrapper = render(CopyButton, options);
    expect(wrapper.vm.$data.success).toBe(false);
  });

  it('data.success should be false by default', () => {
    const wrapper = render(CopyButton, options);
    expect(wrapper.vm.$data.success).toBe(false);
  });

  it('should set data.success to true', () => {
    const wrapper = render(CopyButton, options);
    wrapper.vm.onCopySuccess(eventData);
    expect(wrapper.vm.$data.success).toBe(true);
  });

  it('should set data.success to back to false after 2s', (done) => {
    const wrapper = render(CopyButton, options);
    wrapper.vm.onCopySuccess(eventData);
    setTimeout(() => {
      expect(wrapper.vm.$data.success).toBe(false);
      done();
    }, 2010);
  });

  it('should call clearSelection', () => {
    const wrapper = render(CopyButton, options);
    wrapper.vm.onCopySuccess(eventData);
    expect(eventData.clearSelection).toHaveBeenCalled();
  });

  it('should dispatch COPY_ATTRIBUTION', () => {
    const wrapper = render(CopyButton, options);
    wrapper.vm.onCopySuccess(eventData);
    expect(dispatchMock).toHaveBeenCalledWith(COPY_ATTRIBUTION, {
      contentType: 'rtf',
      content: eventData.text,
    });
  });
});
