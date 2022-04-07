import { render, screen } from '@testing-library/vue'

import VLicense from '~/components/VLicense/VLicense.vue'

describe('VLicense', () => {
  let options = {
    props: {
      license: 'by',
    },
    mocks: {
      $nuxt: {
        context: {
          i18n: { t: (val) => val },
        },
      },
    },
  }

  it('should render the license name and icons', () => {
    const { container } = render(VLicense, options)
    const licenseName = screen.getByLabelText('license-readable-names.by')
    expect(licenseName).toBeInTheDocument()
    const licenseIcons = container.querySelectorAll('svg')
    expect(licenseIcons).toHaveLength(2) // 'CC' and 'BY' icons
  })

  it('should render only the license icons', () => {
    options.props.hideName = true
    const { container } = render(VLicense, options)
    const licenseName = screen.queryByLabelText('license-readable-names.by')
    expect(licenseName).not.toBeVisible()
    const licenseIcons = container.querySelectorAll('svg')
    expect(licenseIcons).toHaveLength(2)
  })

  it('should have background filled with black text', () => {
    options.props.bgFilled = true
    const { container } = render(VLicense, options)
    const licenseIcons = container.querySelectorAll('svg')
    expect(licenseIcons).toHaveLength(2)
    licenseIcons.forEach((icon) => {
      expect(icon).toHaveClass('bg-filled', 'text-black')
    })
  })
})
