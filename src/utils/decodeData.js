export default function decodeData(data) {
  if (data) {
    const regex = /\\x([\d\w]{2})/gi;
    const temp = data.replace(regex, (match, grp) => String.fromCharCode(parseInt(grp, 16)));
    const res = decodeURI(temp);
    return res;
  }
  return '';
}
