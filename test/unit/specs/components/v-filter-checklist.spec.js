import { createLocalVue } from '@vue/test-utils'
import { fireEvent, render, screen } from '@testing-library/vue'

import { PiniaVuePlugin, createPinia } from 'pinia'

import FilterChecklist from '~/components/VFilters/VFilterChecklist'

describe('FilterChecklist', () => {
  let options = {}
  let props = null
  let localVue = null
  let pinia

  beforeEach(() => {
    localVue = createLocalVue()
    localVue.use(PiniaVuePlugin)
    pinia = createPinia()

    props = {
      options: [{ code: 'foo', name: 'bar', checked: false }],
      title: 'Foo',
      filterType: 'bar',
      disabled: false,
    }
    options = {
      localVue,
      pinia,
      propsData: props,
    }
  })

  it('should render correct contents', async () => {
    const { container } = render(FilterChecklist, options)
    const checkbox = screen.getByRole('checkbox', {
      checked: false,
      label: /bar/i,
    })
    expect(checkbox).toBeTruthy()
    expect(container.querySelector('svg')).not.toBeVisible()

    await fireEvent.click(checkbox)
    expect(container.querySelector('svg')).toBeVisible()
  })
})
