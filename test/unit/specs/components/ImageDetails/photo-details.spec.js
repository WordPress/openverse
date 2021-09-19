import PhotoDetails from '~/components/ImageDetails/PhotoDetails'
import {
  DETAIL_PAGE_EVENTS,
  SEND_DETAIL_PAGE_EVENT,
} from '~/constants/usage-data-analytics-types'
import render from '../../../test-utils/render'
import i18n from '../../../test-utils/i18n'
import { REPORT_CONTENT, USAGE_DATA } from '~/constants/store-modules'
import { TOGGLE_REPORT_FORM_VISIBILITY } from '~/constants/mutation-types'

const stubs = {
  LegalDisclaimer: true,
  ImageAttribution: true,
  ContentReportForm: true,
  ReuseSurvey: true,
  ImageSocialShare: true,
  ImageInfo: true,
}

describe('PhotoDetails', () => {
  let options = null
  let props = null
  let storeState = null
  let commitMock = null
  let dispatchMock = null

  const $t = (key) => i18n.messages[key]

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
      socialSharingEnabled: true,
    }

    commitMock = jest.fn()
    dispatchMock = jest.fn()

    storeState = {
      $store: {
        commit: commitMock,
        dispatch: dispatchMock,
        state: {
          isReportFormVisible: false,
        },
      },
    }

    options = {
      propsData: props,
      stubs,
      mocks: {
        ...storeState,
        $t,
      },
    }
  })

  it('should render correct contents', () => {
    const wrapper = render(PhotoDetails, options)
    expect(wrapper.find('.photo_image').element).toBeDefined()
    expect(wrapper.find('[data-testid="image-info"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="image-attribution"]').exists()).toBe(
      true
    )
    expect(wrapper.find('[data-testid="social-share"]').exists()).toBe(true)
  })

  it('should render social sharing buttons', () => {
    const wrapper = render(PhotoDetails, options)
    expect(wrapper.find('[data-testid="social-share"]').exists()).toBe(true)
  })

  it('should not render social sharing buttons when social sharing is disabled', () => {
    options.propsData.socialSharingEnabled = false
    const wrapper = render(PhotoDetails, options)
    expect(wrapper.find('[data-testid="social-share"]').exists()).toBe(false)
  })

  it('should generate license name', () => {
    const wrapper = render(PhotoDetails, options)
    expect(wrapper.vm.fullLicenseName).toBe('CC BY 1.0')
  })

  it('should generate CC-0 license name', () => {
    options.propsData.image.license = 'cc0'
    const wrapper = render(PhotoDetails, options)
    expect(wrapper.vm.fullLicenseName).toBe('CC0 1.0')
  })

  it('should generate CC-0 license name when license is CC0 uppercase', () => {
    options.propsData.image.license = 'CC0'
    const wrapper = render(PhotoDetails, options)
    expect(wrapper.vm.fullLicenseName).toBe('CC0 1.0')
  })

  it('renders link back to search results if enabled', () => {
    options.propsData.shouldShowBreadcrumb = true
    const wrapper = render(PhotoDetails, options)
    expect(wrapper.find('.photo_breadcrumb').element).toBeDefined()
  })

  it('doesnt render link back to search results if disabled', () => {
    options.propsData.shouldShowBreadcrumb = false
    const wrapper = render(PhotoDetails, options)
    expect(wrapper.find('.photo_breadcrumb').element).toBeUndefined()
  })

  it('renders image title', () => {
    const wrapper = render(PhotoDetails, options)
    expect(wrapper.html()).toContain(props.image.title)
  })

  it('renders creator name', () => {
    const wrapper = render(PhotoDetails, options)
    expect(wrapper.html()).toContain(props.image.creator)
  })

  it('redirects back when clicking on the back to results link', async () => {
    const routerMock = {
      push: jest.fn(),
      back: jest.fn(),
    }
    const routeMock = {
      params: {
        location: window.scrollY,
      },
    }
    const opts = {
      propsData: {
        ...props,
        shouldShowBreadcrumb: true,
        query: {
          q: 'foo',
        },
      },
      stubs,
      mocks: {
        $router: routerMock,
        $route: routeMock,
        ...storeState,
        $t,
      },
    }
    const wrapper = render(PhotoDetails, opts)
    const link = wrapper.find('.photo_breadcrumb')
    await link.trigger('click')

    expect(routerMock.back).toHaveBeenCalled()
  })

  it('should toggle visibility of report form on report button click', async () => {
    const wrapper = render(PhotoDetails, options)
    const button = wrapper.find('.report')
    await button.trigger('click')

    expect(commitMock).toHaveBeenCalledWith(
      `${REPORT_CONTENT}/${TOGGLE_REPORT_FORM_VISIBILITY}`
    )
  })

  it('report form should be invisible by default', () => {
    const wrapper = render(PhotoDetails, options)

    expect(
      wrapper.find('[data-testid="content-report-form"]').element
    ).not.toBeDefined()
  })

  it('report form should be visible when isReportFormVisible is true', () => {
    storeState.$store.state.isReportFormVisible = true
    const wrapper = render(PhotoDetails, options)

    expect(wrapper.find('#content-report-form')).toBeDefined()
  })

  it('should dispatch SOURCE_CLICKED on source link clicked', () => {
    const wrapper = render(PhotoDetails, options)
    wrapper.vm.onPhotoSourceLinkClicked()

    expect(dispatchMock).toHaveBeenCalledWith(
      `${USAGE_DATA}/${SEND_DETAIL_PAGE_EVENT}`,
      {
        eventType: DETAIL_PAGE_EVENTS.SOURCE_CLICKED,
        resultUuid: props.image.id,
      }
    )
  })
})
