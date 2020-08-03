import initSentry from '@/sentry/initSentry'

describe('init sentry', () => {
  it('initializes Sentry if params are correct', () => {
    const sentryMock = {
      init: jest.fn(),
      configureScope: jest.fn(),
    }

    initSentry({ Sentry: sentryMock, dsn: 'foo' })

    expect(sentryMock.init).toHaveBeenCalled()
  })

  it('doesnt initialize Sentry if dsn is missing', () => {
    const sentryMock = {
      init: jest.fn(),
      configureScope: jest.fn(),
    }

    initSentry({ Sentry: sentryMock, dsn: null })

    expect(sentryMock.init).not.toHaveBeenCalled()
  })

  it('doesnt throw if Sentry object is missing', () => {
    const init = () => initSentry({ Sentry: null, dsn: 'foo' })

    expect(init).not.toThrow()
  })
})
