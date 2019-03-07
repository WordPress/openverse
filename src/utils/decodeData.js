export default function decodeData(data) {
  if (data) {
    const regexASCII = /\\x([\d\w]{2})/gi;
    const ascii = data.replace(regexASCII, (match, grp) => String.fromCharCode(parseInt(grp, 16)));
    const regexUni = /\\u([\d\w]{4})/gi;
    const uni = ascii.replace(regexUni, (match, grp) => String.fromCharCode(parseInt(grp, 16)));
    const res = decodeURI(uni);
    return res;
  }
  return '';
}
