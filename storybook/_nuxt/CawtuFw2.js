import{a as u}from"./MbisPaIn.js";import{V as o}from"./C3ezsDWb.js";import"./Cb7Zuqx8.js";import{h as c}from"./Bf-AzR54.js";import"./D9JVarWf.js";import"./Cbz4n-D4.js";import"./BTMV7jrV.js";import"./4JVUVGS7.js";import"./BtGjuzI1.js";import"./53t0DvQJ.js";import"./DhTbjJlp.js";import"./Dbp9NDS0.js";import"./CaLJbFDg.js";import"./OXefpJAj.js";import"./D0sNZIq0.js";import"./LrXbMvc1.js";import"./CXyLtIA_.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},a=new e.Error().stack;a&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[a]="e38abed1-2f61-4974-854b-71a49a897443",e._sentryDebugIdIdentifier="sentry-dbid-e38abed1-2f61-4974-854b-71a49a897443")}catch{}})();const O={title:"Components/Audio track/Audio control",component:o,argTypes:{status:{options:u,control:"select"},size:{options:["small","medium","large"],control:"select"},onToggle:{action:"toggle"}}},l={render:e=>({components:{VAudioControl:o},setup(){return()=>c(o,e)}})},t={...l,name:"Default",args:{status:"playing",size:"large"}},r={...l,name:"Disabled",args:{disabled:!0,status:"playing",size:"medium"}};var s,n,i;t.parameters={...t.parameters,docs:{...(s=t.parameters)==null?void 0:s.docs,source:{originalSource:`{
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
