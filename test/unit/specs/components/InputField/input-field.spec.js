import { render, screen } from '@testing-library/vue'

import VInputField from '~/components/VInputField/VInputField.vue'

describe('VInputField', () => {
  xit('should render an `input` element with type="text"', () => {
    render(VInputField, {
      attrs: {
        placeholder: 'Enter some text',
      },
      propsData: {
        fieldId: 'input-id',
        labelText: 'Label',
      },
    })
    screen.debug()
    const element = screen.getByPlaceholderText('Enter some text')

    expect(element.tagName).toBe('INPUT')
    expect(element).toHaveAttribute('type', 'text')
  })

  xit('should allow changing the type', () => {
    render(VInputField, {
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
    render(VInputField, {
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
    render(VInputField, {
      propsData: {
        fieldId: 'input-id',
        labelText: 'Label',
      },
    })

    const element = screen.getByLabelText('Label')

    expect(element.tagName).toBe('INPUT')
  })
})
