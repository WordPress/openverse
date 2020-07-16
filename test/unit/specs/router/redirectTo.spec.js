import redirectTo from '@/router/redirectTo'

describe('redirectTo', () => {
  const routerMock = {
    push: jest.fn(),
    replace: jest.fn(),
  }
  const redirect = redirectTo(routerMock)

  it('calls router.push if replace param is false', () => {
    redirect('foo')

    expect(routerMock.push).toHaveBeenCalledWith('foo')
  })

  it('calls router.replace if replace param is true', () => {
    redirect('foo', true)

    expect(routerMock.replace).toHaveBeenCalledWith('foo')
  })
})
