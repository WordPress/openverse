import { render, fireEvent } from '@testing-library/vue'

import Dropdown from '~/components/Dropdown'

describe('Dropdown', () => {
  let options = {}
  let props = null
  beforeEach(() => {
    props = {
      filter: [{ text: 'Code is Poetry' }],
      filterType: 'bar',
      text: 'Dropdown',
    }
    options = {
      propsData: props,
      scopedSlots: {
        default: `<a data-testid="dropdown-item" @focus="props.onFocus()">WordPress.org</a>`,
      },
    }
  })

  it('should visually hide the dropdown when not focused', () => {
    const { getByRole } = render(Dropdown, options)
    const dropdownWrapper = getByRole('menu')
    expect(dropdownWrapper).not.toHaveClass('visible')
  })

  it('should be visible when the container is focused', async () => {
    const { container, getByRole } = render(Dropdown, options)
    await fireEvent.focus(container.firstChild)
    const dropdownWrapper = getByRole('menu')
    expect(dropdownWrapper).toHaveClass('visible')
  })

  it('should be visible when the dropdown items are focused', async () => {
    const { getByTestId, getByRole } = render(Dropdown, options)
    const dropdownItem = getByTestId('dropdown-item')
    await fireEvent.focus(dropdownItem)
    const dropdownWrapper = getByRole('menu')
    expect(dropdownWrapper).toHaveClass('visible')
  })
})
