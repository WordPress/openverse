import{_ as s,V as t}from"./DTH7ZaUR.js";import{_ as n}from"./CmGhaUYw.js";import"./DzKe1FZy.js";import{h as e}from"./Bf-AzR54.js";import"./BlmTnMLw.js";import"./2X7CKgv5.js";import"./DJpKulq8.js";import"./RE842jSx.js";import"./Mi53UD0-.js";import"./BdGbGJtZ.js";import"./KaIp0RKv.js";import"./Imyqroa4.js";import"./sL22Kbl4.js";import"./CYExI-7Z.js";import"./DhTbjJlp.js";import"../sb-preview/runtime.js";(function(){try{var a=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},l=new a.Error().stack;l&&(a._sentryDebugIds=a._sentryDebugIds||{},a._sentryDebugIds[l]="1043cb74-bb82-486d-8bc4-cdd8bc5e896e",a._sentryDebugIdIdentifier="sentry-dbid-1043cb74-bb82-486d-8bc4-cdd8bc5e896e")}catch{}})();const b={render:a=>({components:{VTabs:s,VTabPanel:n,VTab:t},setup(){return()=>e(s,{...a},{tabs:()=>[e(t,{id:"1"},{default:()=>"Tab1"}),e(t,{id:"2"},{default:()=>"Tab2"}),e(t,{id:"3"},{default:()=>"Tab3"})],default:()=>[e(n,{id:"1"},{default:()=>"Page 1 content"}),e(n,{id:"2"},{default:()=>"Page 2 content"}),e(n,{id:"3"},{default:()=>"Page 3 content"})]})}})},k={component:s,subcomponents:{VTabPanel:n,VTab:t},title:"Components/VTabs",argTypes:{variant:{options:["bordered","plain"],control:{type:"radio"}},onClose:{action:"close"},onChange:{action:"change"}}},r={...b,name:"Default",args:{label:"Default tabs story",selectedId:"1"}},o={...b,name:"Manual plain tabs",args:{label:"Manual plain tabs",selectedId:"1",manual:!0,variant:"plain"}};var d,i,p;r.parameters={...r.parameters,docs:{...(d=r.parameters)==null?void 0:d.docs,source:{originalSource:`{
  ...Template,
  name: "Default",
  args: {
    label: "Default tabs story",
    selectedId: "1"
  }
}`,...(p=(i=r.parameters)==null?void 0:i.docs)==null?void 0:p.source}}};var c,m,u;o.parameters={...o.parameters,docs:{...(c=o.parameters)==null?void 0:c.docs,source:{originalSource:`{
  ...Template,
  name: "Manual plain tabs",
  args: {
    label: "Manual plain tabs",
    selectedId: "1",
    manual: true,
    variant: "plain"
  }
}`,...(u=(m=o.parameters)==null?void 0:m.docs)==null?void 0:u.source}}};const O=["Default","ManualPlainTabs"];export{r as Default,o as ManualPlainTabs,O as __namedExportsOrder,k as default};
