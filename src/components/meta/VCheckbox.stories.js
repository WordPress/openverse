import VCheckbox from '~/components/VCheckbox'
import VLicense from '~/components/License/VLicense'

export default {
  title: 'Components/VCheckbox',
  component: VCheckbox,
}

const SimpleCheckboxStory = (args, { argTypes }) => {
  return {
    template: `<div class="flex flex-col">
    <VCheckbox v-bind="$props" @change="handleChange" class="mb-4">Code is Poetry</VCheckbox>
    <p>Checkbox is {{isChecked ? '' : 'NOT ' }}checked.</p>
    <p>\`@change\` event payload: </p><pre class="ps-0">{{ payload }}</pre>
    </div>`,
    components: { VCheckbox },
    data: () => ({
      isChecked: args.checked,
      payload: null,
    }),
    props: Object.keys(argTypes),
    methods: {
      handleChange(params) {
        this.isChecked = params.checked
        this.payload = params
      },
    },
  }
}

const DisabledCheckboxStory = (args, { argTypes }) => ({
  template: `<fieldset><legend>Use</legend><VCheckbox v-bind="$props">Use commercially</VCheckbox></fieldset>`,
  components: { VCheckbox },
  props: Object.keys(argTypes),
})

const LicenseCheckboxStory = (args, { argTypes }) => ({
  template: `<VCheckbox v-bind="$props" @change="onChange">
  <VLicense license="by-nc" class="me-4"/>
  <span >Checked: {{ isChecked }}</span>
  </VCheckbox>`,
  components: { VCheckbox, VLicense },
  data: () => ({
    isChecked: args.checked,
  }),
  props: Object.keys(argTypes),
  methods: {
    onChange(params) {
      window.alert('License checkbox checked! ' + JSON.stringify(params))
      this.isChecked = params.checked
    },
  },
})

export const Default = SimpleCheckboxStory.bind({})
Default.args = {
  id: 'simple',
  checked: true,
  name: 'checkboxes',
}

export const DisabledCheckbox = DisabledCheckboxStory.bind({})
DisabledCheckbox.args = {
  id: 'disabled',
  checked: false,
  name: 'use',
  disabled: true,
}

export const LicenseCheckbox = LicenseCheckboxStory.bind({})
LicenseCheckbox.args = {
  id: 'license',
  checked: false,
  name: 'checkboxes',
}
