import MediaProviderService from '~/data/media-provider-service'

export default function getProviderLogo(providerName, mediaType = 'image') {
  const provider = MediaProviderService.getProviderInfo(providerName, mediaType)
  if (provider) {
    const logo = provider.logo
    const logoUrl = require(`@/assets/${logo}`)
    return logoUrl
  }

  return ''
}
