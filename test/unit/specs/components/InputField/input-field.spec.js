import { render, screen } from '@testing-library/vue'

import InputField from '~/components/InputField/InputField.vue'

describe('InputField', () => {
  it('should render an `input` element with type="text"', () => {
    render(InputField, {
      attrs: {
        placeholder: 'Enter some text',
      },
      propsData: {
        fieldId: 'input-id',
        labelText: 'Label',
      },
    })

    const element = screen.getByPlaceholderText('Enter some text')

    expect(element.tagName).toBe('INPUT')
    expect(element).toHaveAttribute('type', 'text')
  })

  it('should allow changing the type', () => {
    render(InputField, {
      attrs: {
        placeholder: 'Enter some number',
        type: 'number',
      },
      propsData: {
        fieldId: 'input-id',
        labelText: 'Label',
      },
    })

    const element = screen.getByPlaceholderText('Enter some number')

    expect(element).toHaveAttribute('type', 'number')
  })

  it('should set the ID on the `input` to allow attaching labels', () => {
    render(InputField, {
      attrs: {
        placeholder: 'Enter some text',
      },
      propsData: {
        fieldId: 'input-id',
        labelText: 'Label',
      },
    })

    const element = screen.getByPlaceholderText('Enter some text')

    expect(element).toHaveAttribute('id', 'input-id')
  })

  it('should render the label text connected to the input field if specified', () => {
    render(InputField, {
      propsData: {
        fieldId: 'input-id',
        labelText: 'Label',
      },
    })

    const element = screen.getByLabelText('Label')

    expect(element.tagName).toBe('INPUT')
  })
})
