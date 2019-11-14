const filterToString = filter =>
  filter
    .filter(f => f.checked)
    .map(filterItem => filterItem.code)
    .join(',');

const filterToQueryData = filterData => ({
  provider: filterToString(filterData.provider),
  lt: filterToString(filterData.licenseTypes),
  imageType: filterToString(filterData.imageTypes),
  extension: filterToString(filterData.extensions),
});

export default filterToQueryData;
