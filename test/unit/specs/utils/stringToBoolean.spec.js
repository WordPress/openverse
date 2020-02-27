import stringToBoolean from '@/utils/stringToBoolean';

describe('stringToBoolean', () => {
  it('returns true', () => {
    let flag = 'true';
    let result = stringToBoolean(flag);
    expect(result).toBe(true);
    flag = 'yes';
    result = stringToBoolean(flag);
    expect(result).toBe(true);
    flag = '1';
    result = stringToBoolean(flag);
    expect(result).toBe(true);
  });

  it('returns false', () => {
    let flag = 'false';
    let result = stringToBoolean(flag);
    expect(result).toBe(false);
    flag = 'no';
    result = stringToBoolean(flag);
    expect(result).toBe(false);
    flag = '0';
    result = stringToBoolean(flag);
    expect(result).toBe(false);
  });
});
