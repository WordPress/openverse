import HomeLicenseFilter from '~/components/HomeLicenseFilter'
import render from '../../test-utils/render'

describe('HomeLicenseFilter', () => {
  let options = {}
  let dispatchMock = null

  beforeEach(() => {
    dispatchMock = jest.fn()
    options = {
      mocks: {
        $store: {
          dispatch: dispatchMock,
          state: {
            filters: {
              licenseTypes: [
                { code: 'commercial', name: 'Commercial usage' },
                { code: 'modification', name: 'Allows modification' },
              ],
            },
          },
        },
      },
    }
  })

  it('renders checkboxes', () => {
    const wrapper = render(HomeLicenseFilter, options)
    expect(wrapper.find('#commercial').element).toBeDefined()
    expect(wrapper.find('#modification').element).toBeDefined()
  })

  it('renders checkboxes', () => {
    const wrapper = render(HomeLicenseFilter, options)
    const commercialChk = wrapper.find('#commercial')

    commercialChk.trigger('click')

    expect(dispatchMock).toHaveBeenCalledWith('TOGGLE_FILTER', {
      code: 'commercial',
      filterType: 'licenseTypes',
    })
  })
})
