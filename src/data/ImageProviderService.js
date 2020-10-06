import ApiService from './ApiService'

const ImageProviderService = {
  /**
   * Implements an endpoint to get image provider statistics.
   * SSR-called
   */
  getProviderStats() {
    return ApiService.get('', 'sources')
  },
  getProviderInfo(providerName) {
    const PROVIDER_NAME_LOOKUP = {
      animaldiversity: {
        logo: 'animaldiversity_logo.png',
      },
      behance: {
        logo: 'behance_logo.svg',
      },
      bio_diversity: {
        logo: 'bhl_logo.png',
      },
      brooklynmuseum: {
        logo: 'brooklyn_museum_logo.png',
      },
      CAPL: {
        logo: 'capl_logo.png',
      },
      clevelandmuseum: {
        logo: 'cleveland.png',
      },
      deviantart: {
        logo: 'deviantart_logo.png',
      },
      digitaltmuseum: {
        logo: 'digitaltmuseum_logo.png',
      },
      europeana: {
        logo: 'europeana_logo.svg',
      },
      flickr: {
        logo: 'flickr_icon.png',
      },
      floraon: {
        logo: 'floraon_logo.png',
      },
      geographorguk: {
        logo: 'geographorguk_logo.gif',
      },
      mccordmuseum: {
        logo: 'mccordmuseum_logo.png',
      },
      met: {
        logo: 'met_logo.png',
      },
      museumsvictoria: {
        logo: 'museumvictoria_logo.png',
      },
      nasa: {
        logo: 'nasa_logo.svg',
      },
      nhl: {
        logo: 'nhm_logo.png',
      },
      phylopic: {
        logo: 'phylopic_logo.png',
      },
      rawpixel: {
        logo: 'rawpixel_logo.png',
      },
      rijksmuseum: {
        logo: 'rijksmuseum_logo.png',
      },
      sciencemuseum: {
        logo: 'sciencemuseum_logo.svg',
      },
      sketchfab: {
        logo: 'sketchfab_logo.png',
      },
      smithsonian: {
        logo: 'smithsonian_logo.svg',
      },
      spacex: {
        logo: 'spacex-logo.svg',
      },
      statensmuseum: {
        logo: 'smk_logo.png',
      },
      svgsilh: {
        logo: 'svg-silh_logo.png',
      },
      thingiverse: {
        logo: 'thingiverse_logo.png',
      },
      thorvaldsensmuseum: {
        logo: 'thorvaldsensmuseum_logo.png',
      },
      wikimedia: {
        logo: 'wikimedia_logo.png',
      },
      WoRMS: {
        logo: 'worms_logo.png',
      },
    }

    return PROVIDER_NAME_LOOKUP[providerName]
  },
}

export default ImageProviderService
