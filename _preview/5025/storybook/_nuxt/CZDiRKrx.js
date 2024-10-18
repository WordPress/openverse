import{_ as o,V as e}from"./Dd0rXUjN.js";import{_ as t}from"./4pe4-dmi.js";import{h as a}from"./lnpB3OcH.js";import"./RevM6cLn.js";import"./DuVMw8T-.js";import"./BvLt3-_D.js";import"./BNurbrIm.js";import"./CFMQYC2y.js";import"./BOX21o1p.js";import"./CtE17snF.js";import"./D-c0xjtQ.js";import"./ZjNmaQpL.js";import"./CuPsdpTl.js";import"./DlAUqK2U.js";const d={render:u=>({components:{VTabs:o,VTabPanel:t,VTab:e},setup(){return()=>a(o,{...u},{tabs:()=>[a(e,{id:"1"},{default:()=>"Tab1"}),a(e,{id:"2"},{default:()=>"Tab2"}),a(e,{id:"3"},{default:()=>"Tab3"})],default:()=>[a(t,{id:"1"},{default:()=>"Page 1 content"}),a(t,{id:"2"},{default:()=>"Page 2 content"}),a(t,{id:"3"},{default:()=>"Page 3 content"})]})}})},x={component:o,subcomponents:{VTabPanel:t,VTab:e},title:"Components/VTabs",argTypes:{variant:{options:["bordered","plain"],control:{type:"radio"}},onClose:{action:"close"},onChange:{action:"change"}}},n={...d,name:"Default",args:{label:"Default tabs story",selectedId:"1"}},r={...d,name:"Manual plain tabs",args:{label:"Manual plain tabs",selectedId:"1",manual:!0,variant:"plain"}};var s,l,i;n.parameters={...n.parameters,docs:{...(s=n.parameters)==null?void 0:s.docs,source:{originalSource:`{
  ...Template,
  name: "Default",
  args: {
    label: "Default tabs story",
    selectedId: "1"
  }
}`,...(i=(l=n.parameters)==null?void 0:l.docs)==null?void 0:i.source}}};var m,p,c;r.parameters={...r.parameters,docs:{...(m=r.parameters)==null?void 0:m.docs,source:{originalSource:`{
  ...Template,
  name: "Manual plain tabs",
  args: {
    label: "Manual plain tabs",
    selectedId: "1",
    manual: true,
    variant: "plain"
  }
}`,...(c=(p=r.parameters)==null?void 0:p.docs)==null?void 0:c.source}}};const S=["Default","ManualPlainTabs"];export{n as Default,r as ManualPlainTabs,S as __namedExportsOrder,x as default};
