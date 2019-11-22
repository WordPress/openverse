const filterToString = filter =>
  filter
    .filter(f => f.checked)
    .map(filterItem => filterItem.code)
    .join(',');

const filterToQueryData = filterData => ({
  provider: filterToString(filterData.providers),
  lt: filterToString(filterData.licenseTypes),
  li: filterToString(filterData.licenses),
  imageType: filterToString(filterData.imageTypes),
  extension: filterToString(filterData.extensions),
  searchBy: filterData.searchBy.creator ? 'creator' : '',
});

export default filterToQueryData;
