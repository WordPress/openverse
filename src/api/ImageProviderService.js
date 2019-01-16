
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
      '500px': {
        name: '500px',
        url: 'https://500px.com',
        logo: '500px_logo.png',
      },
      animaldiversity: {
        name: 'Animal Diversity Web',
        url: 'https://animaldiversity.org',
        logo: 'animaldiversity_logo.png',
      },
      behance: {
        name: 'Behance',
        url: 'https://www.behance.net',
        logo: 'behance_logo.svg',
      },
      brooklynmuseum: {
        name: 'Brooklyn Museum',
        url: 'https://www.brooklynmuseum.org/',
        logo: '',
      },
      clevelandmuseum: {
        name: 'Cleveland Museum of Art',
        url: 'http://www.clevelandart.org/',
        logo: '',
      },
      deviantart: {
        name: 'DeviantArt',
        url: 'https://www.deviantart.com',
        logo: 'deviantart_logo.png',
      },
      digitaltmuseum: {
        name: 'Digitalt Museum',
        url: 'https://digitaltmuseum.org',
        logo: 'digitaltmuseum_logo.png',
      },
      eol: {
        name: 'Encyclopedia of Life',
        url: 'http://eol.org',
        logo: 'eol_logo.png',
      },
      flickr: {
        name: 'Flickr',
        url: 'https://www.flickr.com',
        logo: 'flickr_icon.png',
      },
      floraon: {
        name: 'Flora-On',
        url: 'http://flora-on.pt',
        logo: 'floraon_logo.png',
      },
      geographorguk: {
        name: 'Geograph® Britain and Ireland',
        url: 'https://www.geograph.org.uk',
        logo: 'geographorguk_logo.gif',
      },
      iha: {
        name: 'IHA Holiday Ads',
        url: 'https://www.iha.com',
        logo: 'iha_logo.png',
      },
      mccordmuseum: {
        name: 'Montreal Social History Museum',
        url: 'https://www.musee-mccord.qc.ca/en/',
        logo: 'mccordmuseum_logo.png',
      },
      met: {
        name: 'Metropolitan Museum of Art',
        url: 'https://www.metmuseum.org',
        logo: 'mccordmuseum_logo.png',
      },
      museumsvictoria: {
        name: 'Museums Victoria',
        url: 'https://collections.museumvictoria.com.au',
        logo: 'museumvictoria_logo.svg',
      },
      nhl: {
        name: 'TODO',
        url: 'https://TODO.org',
        logo: '',
      },
      nypl: {
        name: 'New York Public Library',
        url: 'https://www.nypl.org',
        logo: 'nypl_logo.svg',
      },
      rijksmuseum: {
        name: 'Rijksmuseum NL',
        url: 'https://www.rijksmuseum.nl/en/',
        logo: 'rijksmuseum_logo.png',
      },
      sciencemuseum: {
        name: 'Science Museum – UK',
        url: 'https://www.sciencemuseum.org.uk',
        logo: 'sciencemuseum_logo.svg',
      },
      thingiverse: {
        name: 'Thingiverse',
        url: 'https://www.thingiverse.com/',
        logo: '',
      },
      WoRMS: {
        name: 'World Register of Marine Species',
        url: 'http://www.marinespecies.org/',
        logo: '',
      },
    };

    return PROVIDER_NAME_LOOKUP[providerName];
  },
};

export default ImageProviderService;
