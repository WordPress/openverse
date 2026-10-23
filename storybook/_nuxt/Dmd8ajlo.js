import{h as u}from"./DmrXErv4.js";import{a as c}from"./B_f6es72.js";import{V as o}from"./jZ59L57J.js";import"./Ceavzuo-.js";import"./QAUZVczv.js";import"./us_YXsMU.js";import"./CdX5GYQk.js";import"./qy-jYTsH.js";import"./BayljJpb.js";import"./DhTbjJlp.js";import"./0xbGHjBU.js";import"./lCCmDL6e.js";import"./Dp2jPxn_.js";import"./CtkidDXQ.js";import"./CMZS2cOm.js";import"./BS_ZT77X.js";import"./Ck0gvfbg.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},a=new e.Error().stack;a&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[a]="2036e2c3-de65-48aa-819d-516b11b4583a",e._sentryDebugIdIdentifier="sentry-dbid-2036e2c3-de65-48aa-819d-516b11b4583a")}catch{}})();const O={title:"Components/Audio track/Audio control",component:o,argTypes:{status:{options:c,control:"select"},size:{options:["small","medium","large"],control:"select"},onToggle:{action:"toggle"}}},l={render:e=>({components:{VAudioControl:o},setup(){return()=>u(o,e)}})},t={...l,name:"Default",args:{status:"playing",size:"large"}},r={...l,name:"Disabled",args:{disabled:!0,status:"playing",size:"medium"}};var s,n,i;t.parameters={...t.parameters,docs:{...(s=t.parameters)==null?void 0:s.docs,source:{originalSource:`{
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
