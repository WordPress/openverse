import { render, screen } from '@testing-library/vue'

import VSearchResultsTitle from '~/components/VSearchResultsTitle.vue'

describe('VSearchResultsTitle', () => {
  let options = {
    props: {
      size: 'large',
    },
    scopedSlots: {
      default: () => 'zack',
    },
  }

  it('should render an h1 tag containing the correct text', async () => {
    render(VSearchResultsTitle, options)
    const button = await screen.findByText('zack')
    expect(button.tagName).toBe('H1')
  })
})
