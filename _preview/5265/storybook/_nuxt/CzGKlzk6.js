import{r as g,h as a}from"./DwwldUEF.js";import{V as n}from"./CBSn_8fJ.js";import"./CWoQmekT.js";import"./9C_OvWUG.js";import"./aezMCrU2.js";import"./tAHCZdDM.js";import"./DhTbjJlp.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},d=new e.Error().stack;d&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[d]="1e97b6b9-aff6-4507-8d4c-bda7b3f9723c",e._sentryDebugIdIdentifier="sentry-dbid-1e97b6b9-aff6-4507-8d4c-bda7b3f9723c")}catch{}})();const I={title:"Components/VRadio",component:n,argTypes:{onChange:{action:"change"}}},v={render:e=>({components:{VRadio:n},setup(){return()=>a("div",a(n,{...e},{default:()=>"Label text"}))}})},l={...v,name:"Default",args:{id:"default",value:"value",modelValue:"modelValue"}},r={...v,name:"Disabled",args:{id:"disabled",value:"value",modelValue:"modelValue",disabled:!0}},o={render:e=>({components:{VRadio:n},setup(){const d=g(e.value);return()=>a("div",a("form",{class:"flex flex-col gap-2 mb-2"},[a(n,{id:"a",name:"test",value:"A",modelValue:d.value},{default:()=>"A"}),a(n,{id:"b",name:"test",value:"B",modelValue:d.value},{default:()=>"B"})]))}}),name:"v-model",args:{id:"a",value:"A"}};var s,t,u;l.parameters={...l.parameters,docs:{...(s=l.parameters)==null?void 0:s.docs,source:{originalSource:`{
  ...Template,
  name: "Default",
  // if same as value, radio is checked
  args: {
    id: "default",
    value: "value",
    modelValue: "modelValue"
  }
}`,...(u=(t=l.parameters)==null?void 0:t.docs)==null?void 0:u.source}}};var m,i,c;r.parameters={...r.parameters,docs:{...(m=r.parameters)==null?void 0:m.docs,source:{originalSource:`{
  ...Template,
  name: "Disabled",
  args: {
    id: "disabled",
    value: "value",
    modelValue: "modelValue",
    disabled: true
  }
}`,...(c=(i=r.parameters)==null?void 0:i.docs)==null?void 0:c.source}}};var p,f,b;o.parameters={...o.parameters,docs:{...(p=o.parameters)==null?void 0:p.docs,source:{originalSource:`{
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
}`,...(b=(f=o.parameters)==null?void 0:f.docs)==null?void 0:b.source}}};const R=["Default","Disabled","VModel"];export{l as Default,r as Disabled,o as VModel,R as __namedExportsOrder,I as default};
