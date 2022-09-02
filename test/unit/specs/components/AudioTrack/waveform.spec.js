import { mount } from '@vue/test-utils'

import { useI18n } from '~/composables/use-i18n'

import VWaveform from '~/components/VAudioTrack/VWaveform.vue'

jest.mock('~/composables/use-i18n', () => ({
  useI18n: jest.fn(),
}))

jest.mock('~/utils/resampling', () => {
  return {
    downsampleArray: jest.fn((data) => data),
    upsampleArray: jest.fn((data) => data),
  }
})

describe('VWaveform', () => {
  let options = null
  let props = null

  beforeEach(() => {
    useI18n.mockImplementation(() => ({ t: (v) => v, tc: (v) => v }))
    props = {
      peaks: [],
      audioId: 'test',
    }

    options = {
      propsData: props,
    }
  })
  afterEach(() => {
    useI18n.mockReset()
  })

  it('should use given peaks when peaks array is provided', () => {
    props.peaks = Array.from({ length: 5 }, () => 0)
    const wrapper = mount(VWaveform, options)
    expect(wrapper.vm.normalizedPeaks.length).toBe(5)
  })

  it('should use random peaks when peaks not set', () => {
    const wrapper = mount(VWaveform, options)
    expect(wrapper.vm.normalizedPeaks.length).toBe(100)
  })

  it('should use random peaks when peaks array is blank', () => {
    props.peaks = null
    const wrapper = mount(VWaveform, options)
    expect(wrapper.vm.normalizedPeaks.length).toBe(100)
  })
})
