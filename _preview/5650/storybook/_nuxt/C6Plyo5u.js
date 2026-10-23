import{h as u}from"./DmrXErv4.js";import{a as c}from"./CJgmNVTT.js";import{V as o}from"./B0BBLk3r.js";import"./Cre_5D1H.js";import"./7Q2jAAAV.js";import"./zcyFsLMi.js";import"./rMKLwKwR.js";import"./Dv0Nl23j.js";import"./Bn7RUpRV.js";import"./DhTbjJlp.js";import"./BRHrr7ck.js";import"./Bpr67t9y.js";import"./B3KNKrKa.js";import"./DWRfakdt.js";import"./CCN4kZnP.js";import"./B_dsH32H.js";import"./OMXwMIS8.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},a=new e.Error().stack;a&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[a]="2036e2c3-de65-48aa-819d-516b11b4583a",e._sentryDebugIdIdentifier="sentry-dbid-2036e2c3-de65-48aa-819d-516b11b4583a")}catch{}})();const O={title:"Components/Audio track/Audio control",component:o,argTypes:{status:{options:c,control:"select"},size:{options:["small","medium","large"],control:"select"},onToggle:{action:"toggle"}}},l={render:e=>({components:{VAudioControl:o},setup(){return()=>u(o,e)}})},t={...l,name:"Default",args:{status:"playing",size:"large"}},r={...l,name:"Disabled",args:{disabled:!0,status:"playing",size:"medium"}};var s,n,i;t.parameters={...t.parameters,docs:{...(s=t.parameters)==null?void 0:s.docs,source:{originalSource:`{
  ...Template,
  name: "Default",
  args: {
    status: "playing",
    size: "large"
  }
}`,...(i=(n=t.parameters)==null?void 0:n.docs)==null?void 0:i.source}}};var m,p,d;r.parameters={...r.parameters,docs:{...(m=r.parameters)==null?void 0:m.docs,source:{originalSource:`{
  ...Template,
  name: "Disabled",
  args: {
    disabled: true,
    status: "playing",
    size: "medium"
  }
}`,...(d=(p=r.parameters)==null?void 0:p.docs)==null?void 0:d.source}}};const j=["Default","Disabled"];export{t as Default,r as Disabled,j as __namedExportsOrder,O as default};
