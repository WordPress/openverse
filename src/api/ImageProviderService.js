
import ApiService from './ApiService';

const ImageProviderService = {
  /**
   * Implements an endpoint to get image provider statistics.
  */
  getProviderStats() {
    return ApiService.get('statistics', 'image');
  },
  getProviderInfo(providerName) {
    const PROVIDER_NAME_LOOKUP = {
      animaldiversity: {
        logo: 'animaldiversity_logo.png',
      },
      behance: {
        logo: 'behance_logo.svg',
      },
      brooklynmuseum: {
        logo: 'brooklyn_museum_logo.png',
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
      flickr: {
        logo: 'flickr_icon.png',
      },
      floraon: {
        logo: 'floraon_logo.png',
      },
      geographorguk: {
        logo: 'geographorguk_logo.gif',
      },
      met: {
        logo: 'met_logo.png',
      },
      museumsvictoria: {
        logo: 'museumvictoria_logo.svg',
      },
      nhl: {
        logo: 'nhm_logo.png',
      },
      rijksmuseum: {
        logo: 'rijksmuseum_logo.png',
      },
      sciencemuseum: {
        logo: 'sciencemuseum_logo.svg',
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
      WoRMS: {
        logo: 'worms_logo.png',
      },
    };

    return PROVIDER_NAME_LOOKUP[providerName];
  },
};

export default ImageProviderService;
