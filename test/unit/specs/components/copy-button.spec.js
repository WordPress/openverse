import CopyButton from '~/components/CopyButton'

import render from '../../test-utils/render'

describe('CopyButton', () => {
  let options = null
  let props = null

  const eventData = {
    text: 'Foo',
    clearSelection: jest.fn(),
  }

  beforeEach(() => {
    props = {
      el: '#foo',
      id: 'foo',
    }
    options = { propsData: props, stubs: ['VButton'] }
  })

  it('should render correct contents', () => {
    const wrapper = render(CopyButton, options)
    expect(wrapper.find('button')).toBeDefined()
  })

  it('data.success should be false by default', () => {
    const wrapper = render(CopyButton, options)
    expect(wrapper.vm.$data.success).toBe(false)
  })

  it('data.success should be false by default', () => {
    const wrapper = render(CopyButton, options)
    expect(wrapper.vm.$data.success).toBe(false)
  })

  it('should set data.success to true', () => {
    const wrapper = render(CopyButton, options)
    wrapper.vm.onCopySuccess(eventData)
    expect(wrapper.vm.$data.success).toBe(true)
  })

  it('should set data.success to back to false after 2s', (done) => {
    const wrapper = render(CopyButton, options)
    wrapper.vm.onCopySuccess(eventData)
    setTimeout(() => {
      expect(wrapper.vm.$data.success).toBe(false)
      done()
    }, 2010)
  })

  it('should call clearSelection', () => {
    const wrapper = render(CopyButton, options)
    wrapper.vm.onCopySuccess(eventData)
    expect(eventData.clearSelection).toHaveBeenCalled()
  })

  it('should emit copied event', () => {
    const wrapper = render(CopyButton, options)
    wrapper.vm.onCopySuccess(eventData)
    expect(wrapper.emitted().copied).toBeTruthy()
  })

  it('should emit copyFailed event', () => {
    const wrapper = render(CopyButton, options)
    wrapper.vm.onCopyError(eventData)
    expect(wrapper.emitted().copyFailed).toBeTruthy()
  })
})
