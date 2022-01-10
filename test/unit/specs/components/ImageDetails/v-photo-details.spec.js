import VPhotoDetails from '~/components/ImageDetails/VPhotoDetails.vue'
import {
  DETAIL_PAGE_EVENTS,
  SEND_DETAIL_PAGE_EVENT,
} from '~/constants/usage-data-analytics-types'
import { fireEvent, render, screen } from '@testing-library/vue'
import { USAGE_DATA } from '~/constants/store-modules'
import { createLocalVue } from '@vue/test-utils'
import Vuex from 'vuex'
import VueI18n from 'vue-i18n'
import messages from '~/locales/en.json'

const i18n = new VueI18n({
  locale: 'en',
  fallbackLocale: 'en',
  messages: { en: messages },
})

describe('PhotoDetails', () => {
  let options = null
  let props = null
  let dispatchMock
  const localVue = createLocalVue()
  localVue.use(Vuex)
  localVue.use(VueI18n)

  beforeEach(() => {
    props = {
      image: {
        id: 0,
        title: 'Title foo',
        provider: 'flickr',
        url: 'foo.bar',
        thumbnail: 'http://foo.bar',
        foreign_landing_url: 'http://foo.bar',
        license: 'BY',
        license_version: '1.0',
        creator: 'John',
        creator_url: 'http://creator.com',
      },
      shouldShowBreadcrumb: true,
      query: {
        q: 'foo',
      },
    }

    dispatchMock = jest.fn()
    const routeMock = {
      params: {
        location: window.scrollY,
      },
    }
    const storeMock = new Vuex.Store({
      modules: {
        search: { namespaced: true, state: {} },
        provider: {
          namespaced: true,
          state: {},
          getters: { getProviderName: (val) => () => val },
        },
        'usage-data': {
          namespaced: true,
          actions: { SEND_DETAIL_PAGE_EVENT: jest.fn() },
        },
      },
    })
    options = {
      localVue,
      propsData: props,
      mocks: {
        $nuxt: {
          context: {
            route: routeMock,
            store: storeMock,
          },
        },
      },
      store: storeMock,
      i18n,
    }
  })

  it('should render correct contents', () => {
    render(VPhotoDetails, options)
    expect(screen.findByAltText(props.image.title)).toBeTruthy()
    expect(screen.queryAllByText(props.image.title)).toHaveLength(1)
  })

  it('should generate license name', () => {
    render(VPhotoDetails, options)
    const licenseName = screen.queryAllByText(/CC BY 1.0/)

    expect(licenseName.length).toEqual(3)
  })

  it('should generate CC-0 license name', () => {
    options.propsData.image.license = 'cc0'
    render(VPhotoDetails, options)
    const licenseElements = screen.queryAllByText(/CC0/i)

    expect(licenseElements.length).toEqual(4)
  })

  it('should generate CC-0 license name when license is CC0 uppercase', () => {
    options.propsData.image.license = 'CC0'
    render(VPhotoDetails, options)
    const licenseElements = screen.queryAllByText(/CC0/i)
    expect(licenseElements.length).toEqual(4)
  })

  it('renders link back to search results if enabled', () => {
    options.propsData.shouldShowBreadcrumb = true
    render(VPhotoDetails, options)

    expect(screen.queryByText(/back/i)).toBeVisible()
  })

  it('doesnt render link back to search results if disabled', async () => {
    options.propsData.shouldShowBreadcrumb = false
    render(VPhotoDetails, options)

    expect(screen.queryByText(/back/i)).toBeNull()
  })

  it('renders image title', () => {
    render(VPhotoDetails, options)

    expect(screen.queryAllByText(props.image.title).length).toEqual(1)
  })

  it('should toggle visibility of report form on report button click', async () => {
    render(VPhotoDetails, options)
    await fireEvent.click(screen.queryByRole('button', { name: /report/i }))

    expect(screen.queryAllByRole('radio').length).toBe(3)
  })

  it('report form should be invisible by default', () => {
    render(VPhotoDetails, options)

    expect(screen.queryAllByRole('radio').length).toEqual(0)
  })

  it('should dispatch SOURCE_CLICKED on source link clicked', async () => {
    options.store.dispatch = dispatchMock
    render(VPhotoDetails, options)
    const sourceLink = screen.queryByTestId('source-button')
    await fireEvent.click(sourceLink)

    expect(dispatchMock).toHaveBeenCalledWith(
      `${USAGE_DATA}/${SEND_DETAIL_PAGE_EVENT}`,
      {
        eventType: DETAIL_PAGE_EVENTS.SOURCE_CLICKED,
        resultUuid: props.image.id,
      }
    )
  })
})
