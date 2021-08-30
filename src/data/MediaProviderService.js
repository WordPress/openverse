import ApiService from './ApiService'
import { IMAGE } from '~/constants/media'

/**
 * Service that calls API to get Media Provider stats
 * @param {('image'|'audio')} mediaType
 * @constructor
 */
const MediaProviderService = (mediaType) => ({
  /**
   * Implements an endpoint to get audio provider statistics.
   * SSR-called
   */
  getProviderStats() {
    try {
      // TODO: use the new 'image/stats' endpoint when it is available in API
      if (mediaType === IMAGE) {
        return ApiService.get('', 'sources')
      }
      return ApiService.get(mediaType, 'stats')
    } catch (err) {
      console.log('Error ', err)
    }
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
      jamendo: {
        logo: 'jamendo_logo.svg',
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

    return PROVIDER_NAME_LOOKUP[mediaType][providerName]
  },
})

export default MediaProviderService
