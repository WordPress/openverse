import HomeLicenseFilter from '~/components/HomeLicenseFilter'
import { render, screen } from '@testing-library/vue'
import { TOGGLE_FILTER } from '~/constants/action-types'
import { FILTER } from '~/constants/store-modules'
import { createLocalVue } from '@vue/test-utils'
import Vuex from 'vuex'

describe('HomeLicenseFilter', () => {
  let options = {}
  let localVue = null
  let dispatchMock = null
  let toggleMock = null
  let storeMock = null

  beforeEach(() => {
    dispatchMock = jest.fn()
    toggleMock = jest.fn()

    localVue = createLocalVue()
    localVue.use(Vuex)
    storeMock = new Vuex.Store({
      modules: {
        filter: {
          namespaced: true,
          actions: {
            // Without this action, we get '[vuex] unknown local action type' error
            [TOGGLE_FILTER]: toggleMock,
          },
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
    })
    options = {
      store: storeMock,
    }
  })

  it('renders checkboxes', () => {
    render(HomeLicenseFilter, options)
    const checkboxes = screen.queryAllByRole('checkbox')
    expect(checkboxes.length).toEqual(2)

    const commercialCheckbox = screen.queryByLabelText('Commercial usage')
    expect(commercialCheckbox).toBeTruthy()

    const modificationCheckbox = screen.queryByLabelText('Allows modification')
    expect(modificationCheckbox).toBeTruthy()
  })

  it('dispatches `TOGGLE_FILTER` when checkboxes selected', async () => {
    storeMock.dispatch = dispatchMock
    render(HomeLicenseFilter, options)
    const commercialCheckbox = screen.queryByLabelText('Commercial usage')
    await commercialCheckbox.click()
    const checked = screen.queryAllByRole('checkbox', { checked: true })

    expect(checked.length).toEqual(1)
    expect(dispatchMock).toHaveBeenCalledWith(`${FILTER}/${TOGGLE_FILTER}`, {
      code: 'commercial',
      filterType: 'licenseTypes',
    })
  })
})
