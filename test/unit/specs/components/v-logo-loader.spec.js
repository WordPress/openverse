import { render, screen } from '@testing-library/vue'

import { useReducedMotion } from '~/composables/use-media-query'

import VLogoLoader from '~/components/VLogoLoader/VLogoLoader.vue'

jest.mock('~/utils/console', () => ({
  warn: jest.fn(),
  log: jest.fn(),
}))

jest.mock('~/composables/use-media-query', () => ({
  useReducedMotion: jest.fn(),
}))

describe('VLogoLoader', () => {
  it('should render the logo', () => {
    render(VLogoLoader)
    const element = screen.getByTestId('logo-loader')
    expect(element).toBeInTheDocument()
  })

  describe('accessibility', () => {
    it('should render differently when the user prefers reduced motion', () => {
      useReducedMotion.mockImplementation(() => true)

      render(VLogoLoader, {
        props: { status: 'loading' },
      })
      const element = screen.getByTestId('logo-loader')
      expect(element).toHaveAttribute('data-prefers-reduced-motion', 'true')
    })
    it('should show the default loading style when no motion preference is set', () => {
      useReducedMotion.mockImplementation(() => false)

      render(VLogoLoader, {
        props: { status: 'loading' },
      })
      const element = screen.getByTestId('logo-loader')
      expect(element).not.toHaveAttribute('data-prefers-reduced-motion')
    })
  })
})
