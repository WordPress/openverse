import analytics from '@/analytics/GoogleAnalytics';
import { CopyTextAttribution } from '@/analytics/events';

describe('GA', () => {
  beforeEach(() => {
    window.ga = jest.fn();
  });

  it('sends event', () => {
    const event = new CopyTextAttribution('foo');
    analytics().sendEvent(event);

    expect(window.ga).toHaveBeenCalledWith('send', event);
  });

  it('sends page view', () => {
    const location = 'foo';
    analytics().updatePageView(location);

    expect(window.ga).toHaveBeenCalledWith('set', 'page', location);
    expect(window.ga).toHaveBeenCalledWith('send', 'pageview');
  });

  it('sends anonymizeIp', () => {
    analytics().anonymizeIpAddress();

    expect(window.ga).toHaveBeenCalledWith('set', 'anonymizeIp', true);
  });

  describe('if doNotTrack is enabled', () => {
    beforeEach(() => {
      navigator.doNotTrack = true;
    });

    it('does not send event', () => {
      const event = new CopyTextAttribution('foo');
      analytics().sendEvent(event);

      expect(window.ga).not.toHaveBeenCalled();
    });

    it('does not send page view', () => {
      const location = 'foo';
      analytics().updatePageView(location);

      expect(window.ga).not.toHaveBeenCalled();
    });

    it('does not send anonymizeIp', () => {
      analytics().anonymizeIpAddress();

      expect(window.ga).not.toHaveBeenCalled();
    });
  });
});
