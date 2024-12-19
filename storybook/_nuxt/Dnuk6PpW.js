import{W as y}from"./BCQtLtfL.js";import{_ as n}from"./u8aaThtY.js";import{V as a}from"./Dg02I9a-.js";import"./CDFarRZf.js";import{h as r}from"./Bf-AzR54.js";import"./D9JVarWf.js";import"./HitohTq8.js";import"./8vSlX9Dy.js";import"./Big7CaLo.js";import"./DhTbjJlp.js";import"./BexTNrA9.js";import"./6POF_SQB.js";import"./olEHfY3b.js";import"./BMvxg2f8.js";import"./CGTJU59N.js";import"./B06Wl6je.js";import"./rZ73O98I.js";import"./shqyu_m_.js";import"./DP0Qqza0.js";import"./bYPJlIeP.js";import"./BF6vVg7M.js";import"./DzAq6MI-.js";import"./DapBWOOs.js";import"./FADBYOvo.js";import"./BkbAmEqc.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},c=new e.Error().stack;c&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[c]="4231e637-9289-40da-98a2-e317e089494b",e._sentryDebugIdIdentifier="sentry-dbid-4231e637-9289-40da-98a2-e317e089494b")}catch{}})();const N={title:"Components/VCheckbox",component:n,decorators:[y],args:{id:"default",name:"Code is Poetry",value:"codeIsPoetry",checked:!1,isSwitch:!1},argTypes:{onChange:{action:"change"}}},g={render:e=>({components:{VCheckbox:n},setup(){return()=>r(n,e,{default:()=>e.name})}})},t={...g,name:"Default"},o={...g,name:"Switch",args:{isSwitch:!0}},s={name:"License Checkbox",render:e=>({components:{VCheckbox:n,VLicense:a},setup(){return()=>r("fieldset",{},[r("legend",{},"License"),r(n,{...e,class:"mb-4"},[r(a,{license:"by-nc",class:"me-4"})])])}}),args:{id:"cc-by",name:"license",value:"cc-by",checked:!0}};var i,m,p;t.parameters={...t.parameters,docs:{...(i=t.parameters)==null?void 0:i.docs,source:{originalSource:`{
  ...Template,
  name: "Default"
}`,...(p=(m=t.parameters)==null?void 0:m.docs)==null?void 0:p.source}}};var d,l,u;o.parameters={...o.parameters,docs:{...(d=o.parameters)==null?void 0:d.docs,source:{originalSource:`{
  ...Template,
  name: "Switch",
  args: {
    isSwitch: true
  }
}`,...(u=(l=o.parameters)==null?void 0:l.docs)==null?void 0:u.source}}};var h,b,f;s.parameters={...s.parameters,docs:{...(h=s.parameters)==null?void 0:h.docs,source:{originalSource:`{
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
}`,...(f=(b=s.parameters)==null?void 0:b.docs)==null?void 0:f.source}}};const Q=["Default","Switch","LicenseCheckbox"];export{t as Default,s as LicenseCheckbox,o as Switch,Q as __namedExportsOrder,N as default};
