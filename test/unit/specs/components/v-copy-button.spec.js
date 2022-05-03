/**
 * This is a short test that only tests the rendered output.
 * Actual copying is being tested by the e2e tests:
 * test/playwright/e2e/attribution.spec.ts
 */
import { render } from '@testing-library/vue'

import VCopyButton from '~/components/VCopyButton.vue'

describe('VCopyButton', () => {
  it('should render correct contents', () => {
    const screen = render(VCopyButton, {
      propsData: {
        el: '#foo',
        id: 'foo',
      },
    })
    expect(screen.getByRole('button')).toHaveTextContent(
      'media-details.reuse.copy-license.copy-text'
    )
  })
})
