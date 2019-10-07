import getParameterByName from '@/utils/getParameterByName';

const filterData = {
  licenses: [
    { code: 'cc0', name: 'CC0', checked: false },
    { code: 'pdm', name: 'Public Domain Mark', checked: false },
    { code: 'by', name: 'BY', checked: false },
    { code: 'by-sa', name: 'BY-SA', checked: false },
    { code: 'by-nc', name: 'BY-NC', checked: false },
    { code: 'by-nd', name: 'BY-ND', checked: false },
    { code: 'by-nc-sa', name: 'BY-NC-SA', checked: false },
    { code: 'by-nc-nd', name: 'BY-NC-ND', checked: false },
  ],
  licenseTypes: [
    { code: 'commercial', name: 'Use for commercial purposes', checked: false },
    { code: 'modification', name: 'Modify or adapt', checked: false },
  ],
  filter: {
    provider: [],
    li: [],
    lt: [],
    searchBy: {
      creator: false,
    },
  },
};

const initialState = (searchParams) => {
  const query = {
    q: getParameterByName('q', searchParams),
    provider: getParameterByName('provider', searchParams).split(',').map(provider => ({
      provider_name: provider,
      checked: true,
    })),
    li: getParameterByName('li', searchParams),
    lt: getParameterByName('lt', searchParams),
    searchBy: getParameterByName('searchBy', searchParams),
  };
};

