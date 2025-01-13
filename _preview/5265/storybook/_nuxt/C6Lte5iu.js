import{h as r}from"./DwwldUEF.js";import{W as y}from"./B22usNta.js";import{_ as n}from"./l1qmPw2d.js";import{V as a}from"./AzfFiQJI.js";import"./CjQ0HQF0.js";import"./Bu-vEs7l.js";import"./Dwl_h6Xz.js";import"./D9b6d0V7.js";import"./DhTbjJlp.js";import"./BkbQYovV.js";import"./CUsfujdM.js";import"./CD6Nr1ia.js";import"./BHl1kxvA.js";import"./Cj2aUrVn.js";import"./Ck0CgHQL.js";import"./BuC5_mLh.js";import"./C6VqcP4x.js";import"./rq0rg1X-.js";import"./BufT_yKp.js";import"./DcMSHMAp.js";import"./DzAq6MI-.js";import"./CiJxsHst.js";import"./D93TPuWH.js";import"./CU-snwr6.js";import"./DNI0JtzU.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},c=new e.Error().stack;c&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[c]="9b9d058f-b919-4435-af71-3d8c0b125e03",e._sentryDebugIdIdentifier="sentry-dbid-9b9d058f-b919-4435-af71-3d8c0b125e03")}catch{}})();const N={title:"Components/VCheckbox",component:n,decorators:[y],args:{id:"default",name:"Code is Poetry",value:"codeIsPoetry",checked:!1,isSwitch:!1},argTypes:{onChange:{action:"change"}}},g={render:e=>({components:{VCheckbox:n},setup(){return()=>r(n,e,{default:()=>e.name})}})},t={...g,name:"Default"},o={...g,name:"Switch",args:{isSwitch:!0}},s={name:"License Checkbox",render:e=>({components:{VCheckbox:n,VLicense:a},setup(){return()=>r("fieldset",{},[r("legend",{},"License"),r(n,{...e,class:"mb-4"},[r(a,{license:"by-nc",class:"me-4"})])])}}),args:{id:"cc-by",name:"license",value:"cc-by",checked:!0}};var i,m,p;t.parameters={...t.parameters,docs:{...(i=t.parameters)==null?void 0:i.docs,source:{originalSource:`{
  ...Template,
  name: "Default"
}`,...(p=(m=t.parameters)==null?void 0:m.docs)==null?void 0:p.source}}};var d,l,u;o.parameters={...o.parameters,docs:{...(d=o.parameters)==null?void 0:d.docs,source:{originalSource:`{
  ...Template,
  name: "Switch",
  args: {
    isSwitch: true
  }
}`,...(u=(l=o.parameters)==null?void 0:l.docs)==null?void 0:u.source}}};var b,f,h;s.parameters={...s.parameters,docs:{...(b=s.parameters)==null?void 0:b.docs,source:{originalSource:`{
  name: "License Checkbox",
  render: args => ({
    components: {
      VCheckbox,
      VLicense
    },
    setup() {
      return () => h("fieldset", {}, [h("legend", {}, "License"), h(VCheckbox, {
        ...args,
        class: "mb-4"
      }, [h(VLicense, {
        license: "by-nc",
        class: "me-4"
      })])]);
    }
  }),
  args: {
    id: "cc-by",
    name: "license",
    value: "cc-by",
    checked: true
  }
}`,...(h=(f=s.parameters)==null?void 0:f.docs)==null?void 0:h.source}}};const Q=["Default","Switch","LicenseCheckbox"];export{t as Default,s as LicenseCheckbox,o as Switch,Q as __namedExportsOrder,N as default};
