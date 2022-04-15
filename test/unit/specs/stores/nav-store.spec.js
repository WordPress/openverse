import { setActivePinia, createPinia } from 'pinia'

import { useNavigationStore } from '~/stores/navigation'

const initialState = {
  isEmbedded: true,
  isReferredFromCc: false,
}

describe('Nav Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })
  it('sets the initial state correctly', () => {
    const navigationStore = useNavigationStore()
    expect(navigationStore.isEmbedded).toEqual(initialState.isEmbedded)
    expect(navigationStore.isReferredFromCc).toEqual(
      initialState.isReferredFromCc
    )
  })

  it.each([true, false, undefined])('sets isEmbedded', (embedded) => {
    const navigationStore = useNavigationStore()
    navigationStore.setIsEmbedded(embedded)
    const expectedValue = embedded ?? true

    expect(navigationStore.isEmbedded).toEqual(expectedValue)
  })

  it.each([true, false, undefined])(
    'sets isReferredFromCc',
    (isReferredFromCc) => {
      const navigationStore = useNavigationStore()
      navigationStore.setIsReferredFromCc(isReferredFromCc)
      const expectedValue = isReferredFromCc ?? true

      expect(navigationStore.isReferredFromCc).toEqual(expectedValue)
    }
  )
})
