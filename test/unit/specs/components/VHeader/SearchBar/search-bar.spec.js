import { render, screen } from '@testing-library/vue'
import { useMatchHomeRoute } from '~/composables/use-match-routes'
import SearchBar from '~/components/VHeader/VSearchBar/VSearchBar.vue'

jest.mock('~/composables/use-match-routes', () => ({
  useMatchHomeRoute: jest.fn(),
}))

const sizes = ['small', 'medium', 'large', 'standalone']

describe('SearchBar', () => {
  let options
  beforeEach(() => {
    options = {
      attrs: { placeholder: 'Enter search query' },
    }
  })

  it.each(sizes)(
    'renders an input field with placeholder and type="search" (%s size)',
    (size) => {
      useMatchHomeRoute.mockImplementation(() => false)
      options.props = { size: size }
      render(SearchBar, options)

      const inputElement = screen.getByPlaceholderText('Enter search query')

      expect(inputElement.tagName).toBe('INPUT')
      expect(inputElement).toHaveAttribute('type', 'search')
      expect(inputElement).toHaveAttribute('placeholder', 'Enter search query')
    }
  )

  it.each(sizes)(
    'renders a button with type="submit", ARIA label and SR text (%s size)',
    (size) => {
      useMatchHomeRoute.mockImplementation(() => false)
      options.props = { size: size }
      render(SearchBar, options)

      const btnElement = screen.getByLabelText('search.search')

      expect(btnElement.tagName).toBe('BUTTON')
      expect(btnElement).toHaveAttribute('type', 'submit')
      expect(btnElement).toHaveAttribute('aria-label', 'search.search')
    }
  )
})
