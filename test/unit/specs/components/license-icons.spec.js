import LicenseIcons from '~/components/LicenseIcons'
import render from '../../test-utils/render'

describe('LicenseIcons', () => {
  let options = null
  let props = null
  let license = null

  beforeEach(() => {
    license = 'by'
    props = {
      license,
    }

    options = {
      propsData: props,
    }
  })

  it('should render correct contents', () => {
    const wrapper = render(LicenseIcons, options)
    expect(wrapper.find('.photo-license-icons').element).toBeDefined()
  })

  it('should generate CC BY icons', () => {
    const wrapper = render(LicenseIcons, options)
    expect(wrapper.find('.cc-logo').element).toBeDefined()
    expect(wrapper.find('.cc-by').element).toBeDefined()
  })

  it('should generate CC BY SA icons', () => {
    props.license = 'by-sa'
    const wrapper = render(LicenseIcons, options)
    expect(wrapper.find('.cc-logo').element).toBeDefined()
    expect(wrapper.find('.cc-by').element).toBeDefined()
    expect(wrapper.find('.cc-sa').element).toBeDefined()
  })

  it('should generate CC BY ND icons', () => {
    props.license = 'by-nd'
    const wrapper = render(LicenseIcons, options)
    expect(wrapper.find('.cc-logo').element).toBeDefined()
    expect(wrapper.find('.cc-by').element).toBeDefined()
    expect(wrapper.find('.cc-nd').element).toBeDefined()
  })

  it('should generate CC0 icons', () => {
    props.license = 'cc0'
    const wrapper = render(LicenseIcons, options)
    expect(wrapper.find('.cc-logo').element).toBeDefined()
    expect(wrapper.find('.cc-zero').element).toBeDefined()
  })

  it('should generate PDM icons', () => {
    props.license = 'pdm'
    const wrapper = render(LicenseIcons, options)
    expect(wrapper.find('.cc-logo').element).toBeDefined()
    expect(wrapper.find('.cc-pd').element).toBeDefined()
  })
})
