import store from '@/store/attribution-store';
import { CopyAttribution, EmbedAttribution, DownloadWatermark } from '@/analytics/events';

describe('Attribution Store', () => {
  describe('actions', () => {
    let googleAnalyticsMock = null;

    beforeEach(() => {
      googleAnalyticsMock = {
        sendEvent: jest.fn(),
      };
    });

    it('COPY_ATTRIBUTION sends copy event', () => {
      const data = {
        content: '<div>foo</div>',
      };
      store.actions(googleAnalyticsMock).COPY_ATTRIBUTION({}, data);

      expect(googleAnalyticsMock.sendEvent).toHaveBeenCalledWith(
        new CopyAttribution(data.content),
      );
    });

    it('EMBED_ATTRIBUTION sends text event', () => {
      store.actions(googleAnalyticsMock).EMBED_ATTRIBUTION();

      expect(googleAnalyticsMock.sendEvent).toHaveBeenCalledWith(
        new EmbedAttribution(),
      );
    });

    it('DOWNLOAD_WATERMARK sends event', () => {
      const data = {
        imageId: 'foo',
      };
      store.actions(googleAnalyticsMock).DOWNLOAD_WATERMARK({}, data);

      expect(googleAnalyticsMock.sendEvent).toHaveBeenCalledWith(
        new DownloadWatermark(data),
      );
    });

    it('DOWNLOAD_WATERMARK sends event with watermark', () => {
      const data = {
        imageId: 'foo',
        shouldWatermark: true,
      };
      store.actions(googleAnalyticsMock).DOWNLOAD_WATERMARK({}, data);

      const eventData = new DownloadWatermark(data);
      expect(eventData.eventAction).toBe('Download watermark | In Attribution Frame');
    });

    it('DOWNLOAD_WATERMARK sends event with metadata', () => {
      const data = {
        imageId: 'foo',
        shouldEmbedMetadata: true,
      };
      store.actions(googleAnalyticsMock).DOWNLOAD_WATERMARK({}, data);

      const eventData = new DownloadWatermark(data);
      expect(eventData.eventAction).toBe('Download watermark | With Attribution Metadata');
    });

    it('DOWNLOAD_WATERMARK sends event with both watermark and metadata', () => {
      const data = {
        imageId: 'foo',
        shouldWatermark: true,
        shouldEmbedMetadata: true,
      };
      store.actions(googleAnalyticsMock).DOWNLOAD_WATERMARK({}, data);

      const eventData = new DownloadWatermark(data);
      expect(eventData.eventAction).toBe('Download watermark | In Attribution Frame | With Attribution Metadata');
    });
  });
});
