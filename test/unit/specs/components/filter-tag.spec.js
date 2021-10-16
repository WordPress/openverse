import FilterTag from '~/components/Filters/FilterTag'
import { render, screen } from '@testing-library/vue'
import userEvent from '@testing-library/user-event'

describe('FilterTag', () => {
  let options = {}
  let props = null
  beforeEach(() => {
    props = {
      code: 'foo',
      label: 'bar-foo',
      filterType: 'bar',
    }
    options = { propsData: props, listeners: { filterChanged: jest.fn() } }
  })

  it('should render correct contents', () => {
    const { container } = render(FilterTag, options)
    expect(container.firstChild).toMatchSnapshot()
  })

  it('should emit filterChanged event', () => {
    render(FilterTag, options)
    userEvent.click(screen.getByRole('button'))
    expect(options.listeners.filterChanged).toHaveBeenCalledWith({
      code: 'foo',
      filterType: 'bar',
    })
  })
})
