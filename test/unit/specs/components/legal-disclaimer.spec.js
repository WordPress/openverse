import LegalDisclaimer from '@/components/LegalDisclaimer';
import render from '../../test-utils/render';

describe('Legal Disclaimer', () => {
  let props = null;
  let options = {};

  beforeEach(() => {
    props = {
      source: 'foo',
      sourceURL: 'http://foo.com',
    };

    options = {
      propsData: props,
    };
  });

  it('displays the legal disclaimer', () => {
    const wrapper = render(LegalDisclaimer, options);
    expect(wrapper.find('.legal-disclaimer').element).toBeDefined();
  });
});
