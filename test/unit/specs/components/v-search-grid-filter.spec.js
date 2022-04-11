import { fireEvent, render, screen } from '@testing-library/vue'
import { createLocalVue } from '@vue/test-utils'
import VueI18n from 'vue-i18n'
import { createPinia, PiniaVuePlugin } from 'pinia'

import { useSearchStore } from '~/stores/search'

import messages from '~/locales/en.json'

import VSearchGridFilter from '~/components/VFilters/VSearchGridFilter.vue'

describe('VSearchGridFilter', () => {
  let options = {}
  let localVue
  let pinia
  let searchStore
  const routerMock = { push: jest.fn() }
  const routeMock = { path: jest.fn() }

  beforeEach(() => {
    localVue = createLocalVue()
    localVue.use(PiniaVuePlugin)
    localVue.use(VueI18n)

    const i18n = new VueI18n({
      locale: 'en',
      fallbackLocale: 'en',
      messages: { en: messages },
    })
    pinia = createPinia()

    options = {
      localVue,
      pinia,
      i18n,
      mocks: {
        $route: routeMock,
        $router: routerMock,
        $nuxt: {
          context: {
            app: { localePath: jest.fn() },
            i18n: { t: (s) => s },
          },
        },
      },
    }
    searchStore = useSearchStore(pinia)
  })

  it('toggles filter', async () => {
    render(VSearchGridFilter, options)
    const checked = screen.queryAllByRole('checkbox', { checked: true })
    expect(checked.length).toEqual(0)
    await fireEvent.click(screen.queryByLabelText(/commercial/i))
    // `getBy` serves as expect because it throws an error if no element is found
    screen.getByRole('checkbox', { checked: true })
    screen.getByLabelText(/commercial/, { checked: true })
  })

  it('clears filters', async () => {
    searchStore.toggleFilter({ filterType: 'licenses', code: 'by' })
    await render(VSearchGridFilter, options)
    // if no checked checkboxes were found, this would raise an error
    screen.getByRole('checkbox', { checked: true })

    await fireEvent.click(screen.getByText('filter-list.clear'))
    const checkedFilters = screen.queryAllByRole('checkbox', { checked: true })
    const uncheckedFilters = screen.queryAllByRole('checkbox', {
      checked: false,
    })

    expect(checkedFilters.length).toEqual(0)
    // Filters are reset with the initial `filterData` for ALL_MEDIA
    expect(uncheckedFilters.length).toEqual(11)
  })
})
