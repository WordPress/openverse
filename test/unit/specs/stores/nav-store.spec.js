import { setActivePinia, createPinia } from 'pinia'

import { useNavStore } from '~/stores/nav'

const initialState = {
  isEmbedded: true,
  isReferredFromCc: false,
}

describe('Nav Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })
  it('sets the initial state correctly', () => {
    const navStore = useNavStore()
    expect(navStore.isEmbedded).toEqual(initialState.isEmbedded)
    expect(navStore.isReferredFromCc).toEqual(initialState.isReferredFromCc)
  })

  it.each([true, false, undefined])('sets isEmbedded', (embedded) => {
    const navStore = useNavStore()
    navStore.setIsEmbedded(embedded)
    const expectedValue = embedded ?? true

    expect(navStore.isEmbedded).toEqual(expectedValue)
  })

  it.each([true, false, undefined])(
    'sets isReferredFromCc',
    (isReferredFromCc) => {
      const navStore = useNavStore()
      navStore.setIsReferredFromCc(isReferredFromCc)
      const expectedValue = isReferredFromCc ?? true

      expect(navStore.isReferredFromCc).toEqual(expectedValue)
    }
  )
})
