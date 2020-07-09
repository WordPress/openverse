import { stringifyUrl } from 'query-string';

/**
 * Accept a base url and a object of query params, and turn it into a formatted url
 * @example q('https://example.com', {cool: 'true', fun: 'yes', other: [1,2,3]}) => `https://example.com?cool=true&fun=yes&other=1,2,3`
 */
const q = (url, queryObject) => stringifyUrl({ url, query: queryObject }, { skipNull: true, arrayFormat: 'comma' });

/**
 * A mapping of each legacy source with its url builder functions for each content type.
 * Urls were based off of deta found here: https://github.com/creativecommons/cccatalog-frontend/issues/315
 */
const legacySourceMap = {
  Europeana: {
    audio(search) {
      return q('https://www.europeana.eu/en/search', {
        page: 1,
        qf: 'TYPE:"SOUND"',
        query: `${search.query} AND RIGHTS:*creative* AND NOT RIGHTS:*nc* AND NOT RIGHTS:*nd*`,
      });
    },
    video(search) {
      return q('https://www.europeana.eu/en/search', {
        page: 1,
        qf: 'TYPE:"VIDEO"',
        query: `${search.query} AND RIGHTS:*creative* AND NOT RIGHTS:*nc* AND NOT RIGHTS:*nd*`,
      });
    },
  },
  'Wikimedia Commons': {
    audio(search) {
      return q('https://commons.wikimedia.org/w/index.php', {
        sort: 'relevance',
        search: `${search.query} filetype:audio`,
        title: 'Special:Search',
        'advancedSearch-current': '{"fields":{"filetype":"audio"}}',
      });
    },
    video(search) {
      return q('https://commons.wikimedia.org/w/index.php', {
        sort: 'relevance',
        search: `${search.query} filetype:video`,
        title: 'Special:Search',
        'advancedSearch-current': '{"fields":{"filetype":"audio"}}',
      });
    },
  },
  Jamendo: {
    audio: '',
  },
  ccMixter: {
    audio: '',
  },
  SoundCloud: {
    audio: '',
  },
  YouTube: {
    video: '',
  },
  'Google Images': {
    image(search) {
      return `https://www.google.com/search?${q({
        as_rights: '(cc_publicdomain%7Ccc_attribute%7Ccc_sharealike).-(cc_noncommercial%7Ccc_nonderived)',
        q: search.query,
      })}`;
    },
  },
  'Open Clip Art Library': {
    image: '',
  },
};

/**
 * getLegacySourceUrl
 *
 * Return a valid url of search results for the provided meta search type (currently audio or video)
 * @param {'image'|'audio'|'video'} type The type of media our meta search is for
 *
 *  */
const getLegacySourceUrl = type => (sourceName, search) => {
  if (!search) throw new Error(`Please provide a valid query to search ${sourceName} for ${type} files.`);

  const source = legacySourceMap[sourceName];
  if (!source) throw new Error(`No data avaliable for provided legacy source: ${sourceName}`);

  const getSourceTypeUrl = source[type];
  if (!getSourceTypeUrl) throw new Error(`${sourceName} does not offer meta search for ${type}`);

  return getSourceTypeUrl(search);
};

export default getLegacySourceUrl;
