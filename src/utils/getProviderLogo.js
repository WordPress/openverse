import ImageProviderService from '../api/ImageProviderService'

export default function getProviderLogo(providerName) {
  const provider = ImageProviderService.getProviderInfo(providerName)
  if (provider) {
    const logo = provider.logo
    const logoUrl = require(`@/assets/${logo}`) // eslint-disable-line global-require, import/no-dynamic-require

    return logoUrl
  }

  return ''
}
