import { render, screen } from '@testing-library/vue'

import SearchBar from '~/components/VHeader/VSearchBar/VSearchBar.vue'

describe('SearchBar', () => {
  it('renders an input field with placeholder and type="search"', () => {
    render(SearchBar, {
      attrs: {
        placeholder: 'Enter search query',
      },
    })

    const inputElement = screen.getByPlaceholderText('Enter search query')

    expect(inputElement.tagName).toBe('INPUT')
    expect(inputElement).toHaveAttribute('type', 'search')
    expect(inputElement).toHaveAttribute('placeholder', 'Enter search query')
  })

  it('renders a button with type="submit", ARIA label and SR text', () => {
    render(SearchBar)

    const btnElement = screen.getByLabelText('search.search')

    expect(btnElement.tagName).toBe('BUTTON')
    expect(btnElement).toHaveAttribute('type', 'submit')
    expect(btnElement).toHaveAttribute('aria-label', 'search.search')
  })
})
