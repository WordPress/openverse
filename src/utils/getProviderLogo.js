import ImageProviderService from '~/data/ImageProviderService'

export default function getProviderLogo(providerName) {
  const provider = ImageProviderService.getProviderInfo(providerName)
  if (provider) {
    const logo = provider.logo
    const logoUrl = require(`@/assets/${logo}`)
    return logoUrl
  }

  return ''
}
