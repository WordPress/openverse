import { render, screen } from '@testing-library/vue'

import { useMatchHomeRoute } from '~/composables/use-match-routes'

import SearchBar from '~/components/VHeader/VSearchBar/VSearchBar.vue'

jest.mock('~/composables/use-match-routes', () => ({
  useMatchHomeRoute: jest.fn(),
}))

const sizes = ['small', 'medium', 'large', 'standalone']
const defaultPlaceholder = 'Enter search query'

describe('SearchBar', () => {
  let options
  beforeEach(() => {
    options = {
      props: { placeholder: defaultPlaceholder, size: 'standalone' },
      mocks: {
        $nuxt: {
          context: {
            app: { $ua: {} },
          },
        },
      },
    }
  })

  it.each(sizes)(
    'renders an input field with placeholder and type="search" (%s size)',
    (size) => {
      useMatchHomeRoute.mockImplementation(() => false)
      options.props.size = size
      render(SearchBar, options)

      const inputElement = screen.getByPlaceholderText(defaultPlaceholder)

      expect(inputElement.tagName).toBe('INPUT')
      expect(inputElement).toHaveAttribute('type', 'search')
      expect(inputElement).toHaveAttribute('placeholder', defaultPlaceholder)
    }
  )

  it.each(sizes)(
    'renders a button with type="submit", ARIA label and SR text (%s size)',
    (size) => {
      useMatchHomeRoute.mockImplementation(() => false)
      options.props.size = size
      render(SearchBar, options)

      const btnElement = screen.getByLabelText('search.search')

      expect(btnElement.tagName).toBe('BUTTON')
      expect(btnElement).toHaveAttribute('type', 'submit')
      expect(btnElement).toHaveAttribute('aria-label', 'search.search')
    }
  )

  describe('placeholder', () => {
    it('should default to hero.search.placeholder', () => {
      delete options.props.placeholder
      render(SearchBar, options)
      expect(
        screen.queryByPlaceholderText('hero.search.placeholder')
      ).not.toBeNull()
    })

    it('should use the prop when provided', () => {
      const placeholder = 'This is a different placeholder from the default'
      options.props.placeholder = placeholder
      render(SearchBar, options)
      expect(screen.queryByPlaceholderText(placeholder)).not.toBeNull()
    })
  })
})
