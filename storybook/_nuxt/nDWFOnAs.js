import{h as c}from"./53SD24Bo.js";import{a as u}from"./BlaBANgC.js";import{V as o}from"./DqEczdWr.js";import"./_bbq3c9C.js";import"./BnbCYJz1.js";import"./xQ8_qGND.js";import"./dvXbmdTd.js";import"./ivjvpZKc.js";import"./DjsporFN.js";import"./DhTbjJlp.js";import"./DlboKt2a.js";import"./Di7dAt70.js";import"./B9k6C3Hw.js";import"./BOewZ2sR.js";import"./D2GrBf-6.js";import"./B_-6Taiq.js";import"./CH5-dTGy.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},s=new e.Error().stack;s&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[s]="01476afb-8fb2-4fd4-bbd8-7cc2dc6005d1",e._sentryDebugIdIdentifier="sentry-dbid-01476afb-8fb2-4fd4-bbd8-7cc2dc6005d1")}catch{}})();const O={title:"Components/Audio track/Audio control",component:o,argTypes:{status:{options:u,control:"select"},size:{options:["small","medium","large"],control:"select"},onToggle:{action:"toggle"}}},l={render:e=>({components:{VAudioControl:o},setup(){return()=>c(o,e)}})},t={...l,name:"Default",args:{status:"playing",size:"large"}},r={...l,name:"Disabled",args:{disabled:!0,status:"playing",size:"medium"}};var a,n,i;t.parameters={...t.parameters,docs:{...(a=t.parameters)==null?void 0:a.docs,source:{originalSource:`{
  ...Template,
  name: "Default",
  args: {
    status: "playing",
    size: "large"
  }
}`,...(i=(n=t.parameters)==null?void 0:n.docs)==null?void 0:i.source}}};var d,m,p;r.parameters={...r.parameters,docs:{...(d=r.parameters)==null?void 0:d.docs,source:{originalSource:`{
  ...Template,
  name: "Disabled",
  args: {
    disabled: true,
    status: "playing",
    size: "medium"
  }
}`,...(p=(m=r.parameters)==null?void 0:m.docs)==null?void 0:p.source}}};const j=["Default","Disabled"];export{t as Default,r as Disabled,j as __namedExportsOrder,O as default};
