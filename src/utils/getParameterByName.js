export default function getParameterByName(key, url) {
  const name = key.replace(/[[\]]/g, '\\$&');
  const regex = new RegExp(`[?&]${name}(=([^&#]*)|&|#|$)`);
  const results = regex.exec(url);
  if (!results || !results[2]) return '';
  return decodeURIComponent(results[2].replace(/\+/g, ' '));
}
