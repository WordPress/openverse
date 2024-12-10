import{V as a}from"./DSzrood5.js";import{G as g,h as e}from"./lKNUlTH_.js";import"./C2lBk38O.js";import"./CuPsdpTl.js";import"./CFMQYC2y.js";import"./DlAUqK2U.js";const R={title:"Components/VRadio",component:a,argTypes:{onChange:{action:"change"}}},V={render:r=>({components:{VRadio:a},setup(){return()=>e("div",e(a,{...r},{default:()=>"Label text"}))}})},n={...V,name:"Default",args:{id:"default",value:"value",modelValue:"modelValue"}},l={...V,name:"Disabled",args:{id:"disabled",value:"value",modelValue:"modelValue",disabled:!0}},o={render:r=>({components:{VRadio:a},setup(){const s=g(r.value);return()=>e("div",e("form",{class:"flex flex-col gap-2 mb-2"},[e(a,{id:"a",name:"test",value:"A",modelValue:s.value},{default:()=>"A"}),e(a,{id:"b",name:"test",value:"B",modelValue:s.value},{default:()=>"B"})]))}}),name:"v-model",args:{id:"a",value:"A"}};var d,t,u;n.parameters={...n.parameters,docs:{...(d=n.parameters)==null?void 0:d.docs,source:{originalSource:`{
  ...Template,
  name: "Default",
  // if same as value, radio is checked
  args: {
    id: "default",
    value: "value",
    modelValue: "modelValue"
  }
}`,...(u=(t=n.parameters)==null?void 0:t.docs)==null?void 0:u.source}}};var m,i,c;l.parameters={...l.parameters,docs:{...(m=l.parameters)==null?void 0:m.docs,source:{originalSource:`{
  ...Template,
  name: "Disabled",
  args: {
    id: "disabled",
    value: "value",
    modelValue: "modelValue",
    disabled: true
  }
}`,...(c=(i=l.parameters)==null?void 0:i.docs)==null?void 0:c.source}}};var p,v,f;o.parameters={...o.parameters,docs:{...(p=o.parameters)==null?void 0:p.docs,source:{originalSource:`{
  render: args => ({
    components: {
      VRadio
    },
    setup() {
      const picked = ref<string>(args.value);
      return () => h("div", h("form", {
        class: "flex flex-col gap-2 mb-2"
      }, [h(VRadio, {
        id: "a",
        name: "test",
        value: "A",
        modelValue: picked.value
      }, {
        default: () => "A"
      }), h(VRadio, {
        id: "b",
        name: "test",
        value: "B",
        modelValue: picked.value
      }, {
        default: () => "B"
      })]));
    }
  }),
  name: "v-model",
  args: {
    id: "a",
    value: "A"
  }
}`,...(f=(v=o.parameters)==null?void 0:v.docs)==null?void 0:f.source}}};const B=["Default","Disabled","VModel"];export{n as Default,l as Disabled,o as VModel,B as __namedExportsOrder,R as default};
