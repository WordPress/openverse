import{h as r}from"./53SD24Bo.js";import{W as y}from"./Cnf0rCZE.js";import{_ as n}from"./C1N7lWe8.js";import{V as a}from"./Bn_c1StJ.js";import"./DxXQfK2h.js";import"./CO_nLv6a.js";import"./DY7Jae7t.js";import"./1q_AdtTO.js";import"./DhTbjJlp.js";import"./DvuKu9Ve.js";import"./7T7Oyunt.js";import"./Ca-grqql.js";import"./Mo01N0st.js";import"./CSqorYok.js";import"./7RO02bE1.js";import"./CJn6N6md.js";import"./DEUQKZ_9.js";import"./BfmvDfJj.js";import"./GK6z1vC-.js";import"./DCBI9Hp4.js";import"./okj3qyDJ.js";import"./BB93wJtT.js";import"./B9Cuo1Ro.js";import"./BQrorSEU.js";import"./B06vE1PI.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},c=new e.Error().stack;c&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[c]="9b9d058f-b919-4435-af71-3d8c0b125e03",e._sentryDebugIdIdentifier="sentry-dbid-9b9d058f-b919-4435-af71-3d8c0b125e03")}catch{}})();const N={title:"Components/VCheckbox",component:n,decorators:[y],args:{id:"default",name:"Code is Poetry",value:"codeIsPoetry",checked:!1,isSwitch:!1},argTypes:{onChange:{action:"change"}}},g={render:e=>({components:{VCheckbox:n},setup(){return()=>r(n,e,{default:()=>e.name})}})},t={...g,name:"Default"},o={...g,name:"Switch",args:{isSwitch:!0}},s={name:"License Checkbox",render:e=>({components:{VCheckbox:n,VLicense:a},setup(){return()=>r("fieldset",{},[r("legend",{},"License"),r(n,{...e,class:"mb-4"},[r(a,{license:"by-nc",class:"me-4"})])])}}),args:{id:"cc-by",name:"license",value:"cc-by",checked:!0}};var i,m,p;t.parameters={...t.parameters,docs:{...(i=t.parameters)==null?void 0:i.docs,source:{originalSource:`{
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
