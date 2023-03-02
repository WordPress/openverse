import { mount } from "@vue/test-utils"

import VToggleSwitch from "~/components/VToggleSwitch/VToggleSwitch.vue"

test("should render a toggle swtich with a string lable", async () => {
    const wrapper = mount(VToggleSwitch, {
        slots: {
            default: "<span>Toggle Switch</span>",
        },
    })

    const toggleSwitch = wrapper.find('input[type="checkbox"]')
    const knob = wrapper.find(".knob")
    const layer = wrapper.find(".layer")

    expect(wrapper.find("span").text()).toBe("Toggle Switch")
    expect(toggleSwitch.exists()).toBe(true)
    expect(knob.exists()).toBe(true)
    expect(layer.exists()).toBe(true)
})

test("should render a checked toggle switch if `checked` is true", () => {
    const wrapper = mount(VToggleSwitch, {
        propsData: {
            checked: true,
        },
    })

    const toggleSwitch = wrapper.find("input:checked")

    expect(toggleSwitch.element.checked).toBe(true)
})

test("should emit change event on change", () => {
    const wrapper = mount(VToggleSwitch)

    wrapper.vm.onChange()
    expect(wrapper.emitted().change).toBeTruthy()
})