import { render, screen } from '@testing-library/vue'
import userEvent from '@testing-library/user-event'
import { PiniaVuePlugin } from 'pinia'
import { createTestingPinia } from '@pinia/testing'
import VueI18n from 'vue-i18n'

import VSourcesTableVue from '~/components/VSourcesTable.vue'

const enMessages = require('~/locales/en.json')

const i18n = new VueI18n({
  locale: 'en',
  fallbackLocale: 'en',
  messages: { en: enMessages },
})

const useMockStore = (vue) => {
  vue.use(PiniaVuePlugin)
  const pinia = createTestingPinia({
    initialState: {
      provider: {
        providers: {
          image: [
            {
              source_name: 'Provider_B',
              display_name: 'Provider B',
              source_url: 'http://yyy.com',
              media_count: 1111,
            },
            {
              source_name: 'Provider_C',
              display_name: 'Provider C',
              source_url: 'www.xxx.com',
              media_count: 2222,
            },
            {
              source_name: 'Provider_A',
              display_name: 'Provider A',
              source_url: 'https://zzz.com',
              media_count: 3333,
            },
          ],
        },
      },
    },
  })
  return { pinia }
}

const configureVue = (vue) => {
  const { pinia } = useMockStore(vue)
  vue.use(VueI18n)

  return {
    i18n,
    pinia,
    /** @todo Create a better mock that can be configured to test this behavior.  */
  }
}

const getTableData = (table) => {
  const data = [...table.rows].map((t) =>
    [...t.children].map((u) => u.textContent.trim())
  )
  // Remove the header row
  data.shift()
  return data
}

describe('VSourcesTable', () => {
  let options

  beforeEach(() => {
    options = {
      propsData: { media: 'image' },
      stubs: ['TableSortIcon', 'VLink'],
      mocks: {
        $nuxt: { context: { i18n } },
      },
    }
  })

  it('should be sorted by display_name ("Source") by default', () => {
    render(VSourcesTableVue, options, configureVue)
    const table = getTableData(screen.getByLabelText('sources.aria.table'))
    const expectedTable = [
      ['Provider A', 'zzz.com', '3,333'],
      ['Provider B', 'yyy.com', '1,111'],
      ['Provider C', 'xxx.com', '2,222'],
    ]
    expect(table).toEqual(expectedTable)
  })

  it('should be sorted by clean url when click on "Domain" header', async () => {
    render(VSourcesTableVue, options, configureVue)
    const domainCell = screen.getByRole('columnheader', {
      name: 'sources.providers.domain',
    })
    await userEvent.click(domainCell)
    const table = getTableData(screen.getByLabelText('sources.aria.table'))
    const expectedTable = [
      ['Provider C', 'xxx.com', '2,222'],
      ['Provider B', 'yyy.com', '1,111'],
      ['Provider A', 'zzz.com', '3,333'],
    ]
    expect(table).toEqual(expectedTable)
  })

  it('should be sorted by media_count when click on "Total items" header', async () => {
    render(VSourcesTableVue, options, configureVue)
    const domainCell = screen.getByRole('columnheader', {
      name: 'sources.providers.item',
    })
    await userEvent.click(domainCell)
    const table = getTableData(screen.getByLabelText('sources.aria.table'))
    const expectedTable = [
      ['Provider B', 'yyy.com', '1,111'],
      ['Provider C', 'xxx.com', '2,222'],
      ['Provider A', 'zzz.com', '3,333'],
    ]
    expect(table).toEqual(expectedTable)
  })
})
