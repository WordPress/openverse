import initSentry from '@/sentry/initSentry'

describe('init sentry', () => {
  it('initializes Sentry if params are correct', () => {
    const sentryMock = {
      init: jest.fn(),
    }

    initSentry(sentryMock, 'foo')

    expect(sentryMock.init).toHaveBeenCalledWith({ dsn: 'foo' })
  })

  it('doesnt initialize Sentry if dsn is missing', () => {
    const sentryMock = {
      init: jest.fn(),
    }

    initSentry(sentryMock, null)

    expect(sentryMock.init).not.toHaveBeenCalled()
  })

  it('doesnt throw if Sentry object is missing', () => {
    const init = () => initSentry(null, 'foo')

    expect(init).not.toThrow()
  })
})
