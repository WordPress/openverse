export const getAudioObj = (overrides = {}) =>
  Object.assign(
    {
      id: 'e19345b8-6937-49f7-a0fd-03bf057efc28',
      title: 'La vie des bêtes',
      foreign_landing_url: 'https://www.jamendo.com/track/11188',
      creator: 'AS-POTIRONT!',
      creator_url: 'https://www.jamendo.com/artist/264/as-potiront',
      url: 'https://mp3d.jamendo.com/download/track/11188/mp32',
      license: 'by-nc-sa',
      license_version: '2.5',
      license_url: 'https://creativecommons.org/licenses/by-nc-sa/2.5/',
      provider: 'jamendo',
      source: 'jamendo',
      filetype: 'mp32',
      tags: [
        {
          name: 'vocal',
        },
        {
          name: 'male',
        },
        {
          name: 'speed_medium',
        },
        {
          name: 'party',
        },
        {
          name: 'cuivres',
        },
      ],
      fields_matched: ['tags.name'],
      thumbnail:
        'https://localhost:8000/v1/audio/e19345b8-6937-49f7-a0fd-03bf057efc28/thumb',
      waveform:
        'https://localhost:8000/v1/audio/e19345b8-6937-49f7-a0fd-03bf057efc28/waveform',
      genres: ['pop', 'rock', 'manouche'],
      detail_url:
        'http://localhost:8000/v1/audio/e19345b8-6937-49f7-a0fd-03bf057efc28',
      related_url:
        'http://localhost:8000/v1/audio/e19345b8-6937-49f7-a0fd-03bf057efc28/recommendations',
    },
    overrides
  )
