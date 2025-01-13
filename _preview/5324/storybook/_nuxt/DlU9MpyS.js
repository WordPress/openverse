import{a as c}from"./CPkmNCsP.js";import{V as o}from"./CWJTnQOn.js";import"./BQ2uyTwE.js";import{h as u}from"./ueSFnAt6.js";import"./dNCV0R31.js";import"./D2P1fKwO.js";import"./CIRXjnDb.js";import"./CFNrPCvG.js";import"./B_AFY9SJ.js";import"./DDGXuWLI.js";import"./DhTbjJlp.js";import"./DKvPnfU5.js";import"./DI2Xpw6B.js";import"./DSEYgdJX.js";import"./A1b6Lb8y.js";import"./BQNGXNMh.js";import"./C4YS0AQy.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},s=new e.Error().stack;s&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[s]="21205728-42f4-4cf1-97df-8eb0c38d3afc",e._sentryDebugIdIdentifier="sentry-dbid-21205728-42f4-4cf1-97df-8eb0c38d3afc")}catch{}})();const O={title:"Components/Audio track/Audio control",component:o,argTypes:{status:{options:c,control:"select"},size:{options:["small","medium","large"],control:"select"},onToggle:{action:"toggle"}}},l={render:e=>({components:{VAudioControl:o},setup(){return()=>u(o,e)}})},t={...l,name:"Default",args:{status:"playing",size:"large"}},r={...l,name:"Disabled",args:{disabled:!0,status:"playing",size:"medium"}};var a,n,i;t.parameters={...t.parameters,docs:{...(a=t.parameters)==null?void 0:a.docs,source:{originalSource:`{
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
