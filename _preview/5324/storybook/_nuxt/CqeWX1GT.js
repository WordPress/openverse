import{_ as s,V as t}from"./B0b92HrV.js";import{_ as n}from"./B7EBVdcD.js";import"./BQ2uyTwE.js";import{h as e}from"./ueSFnAt6.js";import"./BOH1sSDC.js";import"./DKvPnfU5.js";import"./DI2Xpw6B.js";import"./DSEYgdJX.js";import"./A1b6Lb8y.js";import"./BQNGXNMh.js";import"./DDGXuWLI.js";import"./C4YS0AQy.js";import"./CFNrPCvG.js";import"./B_AFY9SJ.js";import"./DhTbjJlp.js";import"../sb-preview/runtime.js";(function(){try{var a=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},l=new a.Error().stack;l&&(a._sentryDebugIds=a._sentryDebugIds||{},a._sentryDebugIds[l]="290419e3-0b62-49c4-a6f9-5cd080d47023",a._sentryDebugIdIdentifier="sentry-dbid-290419e3-0b62-49c4-a6f9-5cd080d47023")}catch{}})();const b={render:a=>({components:{VTabs:s,VTabPanel:n,VTab:t},setup(){return()=>e(s,{...a},{tabs:()=>[e(t,{id:"1"},{default:()=>"Tab1"}),e(t,{id:"2"},{default:()=>"Tab2"}),e(t,{id:"3"},{default:()=>"Tab3"})],default:()=>[e(n,{id:"1"},{default:()=>"Page 1 content"}),e(n,{id:"2"},{default:()=>"Page 2 content"}),e(n,{id:"3"},{default:()=>"Page 3 content"})]})}})},k={component:s,subcomponents:{VTabPanel:n,VTab:t},title:"Components/VTabs",argTypes:{variant:{options:["bordered","plain"],control:{type:"radio"}},onClose:{action:"close"},onChange:{action:"change"}}},r={...b,name:"Default",args:{label:"Default tabs story",selectedId:"1"}},o={...b,name:"Manual plain tabs",args:{label:"Manual plain tabs",selectedId:"1",manual:!0,variant:"plain"}};var i,d,p;r.parameters={...r.parameters,docs:{...(i=r.parameters)==null?void 0:i.docs,source:{originalSource:`{
  ...Template,
  name: "Default",
  args: {
    label: "Default tabs story",
    selectedId: "1"
  }
}`,...(p=(d=r.parameters)==null?void 0:d.docs)==null?void 0:p.source}}};var m,c,u;o.parameters={...o.parameters,docs:{...(m=o.parameters)==null?void 0:m.docs,source:{originalSource:`{
  ...Template,
  name: "Manual plain tabs",
  args: {
    label: "Manual plain tabs",
    selectedId: "1",
    manual: true,
    variant: "plain"
  }
}`,...(u=(c=o.parameters)==null?void 0:c.docs)==null?void 0:u.source}}};const O=["Default","ManualPlainTabs"];export{r as Default,o as ManualPlainTabs,O as __namedExportsOrder,k as default};
