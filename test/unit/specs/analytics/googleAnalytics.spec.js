import GoogleAnalytics from '@/analytics/googleAnalytics';
import { CopyTextAttribution } from '@/analytics/events';

describe('GA', () => {
  it('sends event', () => {
    window.ga = jest.fn();

    const event = new CopyTextAttribution('foo');
    GoogleAnalytics.sendEvent(event);

    expect(window.ga).toHaveBeenCalledWith('send', event);
  });
});
