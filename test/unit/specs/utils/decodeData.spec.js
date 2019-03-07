import decodeData from '@/utils/decodeData';

describe('decodeData', () => {
  it('returns empty string for empty string', () => {
    const data = "";

    expect(decodeData(data)).toEqual("");
  });

  it('returns empty string for undefined data', () => {
    const data = undefined;
    const empty="";

    expect(decodeData(data)).toEqual(""); 
  });

  it('decodes unicode strings', () => {
    const data = 's\\xe9'

    expect(decodeData(data)).toBe('s\xe9');
  });
});
