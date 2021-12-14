import VScrollButton from '~/components/VScrollButton'
import { render, screen } from '@testing-library/vue'

describe('Scroll button', () => {
  it('should render a scroll button', () => {
    const { container } = render(VScrollButton)
    expect(screen.getByRole('button')).toBeTruthy()
    expect(screen.getByLabelText(/scroll/i)).toBeTruthy()
    expect(container.querySelectorAll('svg').length).toEqual(1)
  })
})
