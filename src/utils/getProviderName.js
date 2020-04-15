export default function getProviderName(providersList, providerCode) {
  if (!providersList) {
    return '';
  }

  const provider = providersList.filter(p => p.source_name === providerCode)[0];

  return provider ? provider.display_name : '';
}
