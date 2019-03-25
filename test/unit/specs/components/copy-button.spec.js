import CopyButton from '@/components/CopyButton';
import render from '../../test-utils/render';

describe('CopyButton', () => {
  let options = null;
  let props = null;
  beforeEach(() => {
    props = {
      toCopy: 'foo',
      contentType: 'bar',
    };
    options = {
      propsData: props,
    };
  });

  it('should render correct contents', () => {
    const wrapper = render(CopyButton, options);
    expect(wrapper.find('button').vm).toBeDefined();
  });
});
