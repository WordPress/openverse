import{h as e}from"./53SD24Bo.js";import{_ as s,V as t}from"./CYxeF2X6.js";import{_ as n}from"./BNEsrME-.js";import"./RQxsyxdU.js";import"./DYa50zxq.js";import"./ByZ6H8Q9.js";import"./oAL5f6fw.js";import"./Cai0IfA4.js";import"./B7ZxQ_gM.js";import"./CGdESDy3.js";import"./C4QhmNcb.js";import"./BALwooav.js";import"./CxzE6WfI.js";import"./BsOxdBIg.js";import"./DhTbjJlp.js";import"../sb-preview/runtime.js";(function(){try{var a=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},l=new a.Error().stack;l&&(a._sentryDebugIds=a._sentryDebugIds||{},a._sentryDebugIds[l]="ec81327a-c29e-4502-8ad8-595e328ebf3a",a._sentryDebugIdIdentifier="sentry-dbid-ec81327a-c29e-4502-8ad8-595e328ebf3a")}catch{}})();const b={render:a=>({components:{VTabs:s,VTabPanel:n,VTab:t},setup(){return()=>e(s,{...a},{tabs:()=>[e(t,{id:"1"},{default:()=>"Tab1"}),e(t,{id:"2"},{default:()=>"Tab2"}),e(t,{id:"3"},{default:()=>"Tab3"})],default:()=>[e(n,{id:"1"},{default:()=>"Page 1 content"}),e(n,{id:"2"},{default:()=>"Page 2 content"}),e(n,{id:"3"},{default:()=>"Page 3 content"})]})}})},k={component:s,subcomponents:{VTabPanel:n,VTab:t},title:"Components/VTabs",argTypes:{variant:{options:["bordered","plain"],control:{type:"radio"}},onClose:{action:"close"},onChange:{action:"change"}}},r={...b,name:"Default",args:{label:"Default tabs story",selectedId:"1"}},o={...b,name:"Manual plain tabs",args:{label:"Manual plain tabs",selectedId:"1",manual:!0,variant:"plain"}};var i,d,p;r.parameters={...r.parameters,docs:{...(i=r.parameters)==null?void 0:i.docs,source:{originalSource:`{
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
