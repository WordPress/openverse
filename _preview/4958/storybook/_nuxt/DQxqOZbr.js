import{W as v}from"./Ch5Cbo_u.js";import{h as F}from"./lKNUlTH_.js";const y={title:"Meta/Focus",decorators:[v]},l=S=>x=>({setup(){return()=>F("div",{class:`h-30 w-30 flex items-center justify-center ${S} ${x.classNames.join(" ")}`,"data-testid":"focus-target",tabindex:"0"},"Focus on me")}}),e={render:l("border border-disabled hover:border-hover").bind({}),name:"Slim transparent",args:{classNames:["focus-slim-tx"]}},r={render:l("bg-tertiary text-over-dark border border-tx").bind({}),name:"Slim filled",args:{classNames:["focus-slim-filled"]}},s={render:l("bg-primary text-over-dark").bind({}),name:"Slim filled borderless",args:{classNames:["focus-slim-borderless-filled"]}},a={render:l("bg-complementary text-default").bind({}),name:"Bold filled",args:{classNames:["focus-bold-filled"]}};var o,t,d;e.parameters={...e.parameters,docs:{...(o=e.parameters)==null?void 0:o.docs,source:{originalSource:`{
  render: GetTemplate("border border-disabled hover:border-hover").bind({}),
  name: "Slim transparent",
  args: {
    classNames: ["focus-slim-tx"]
  }
}`,...(d=(t=e.parameters)==null?void 0:t.docs)==null?void 0:d.source}}};var n,i,m;r.parameters={...r.parameters,docs:{...(n=r.parameters)==null?void 0:n.docs,source:{originalSource:`{
  render: GetTemplate("bg-tertiary text-over-dark border border-tx").bind({}),
  name: "Slim filled",
  args: {
    classNames: ["focus-slim-filled"]
  }
}`,...(m=(i=r.parameters)==null?void 0:i.docs)==null?void 0:m.source}}};var c,p,b;s.parameters={...s.parameters,docs:{...(c=s.parameters)==null?void 0:c.docs,source:{originalSource:`{
  render: GetTemplate("bg-primary text-over-dark").bind({}),
  name: "Slim filled borderless",
  args: {
    classNames: ["focus-slim-borderless-filled"]
  }
}`,...(b=(p=s.parameters)==null?void 0:p.docs)==null?void 0:b.source}}};var u,f,g;a.parameters={...a.parameters,docs:{...(u=a.parameters)==null?void 0:u.docs,source:{originalSource:`{
  render: GetTemplate("bg-complementary text-default").bind({}),
  name: "Bold filled",
  args: {
    classNames: ["focus-bold-filled"]
  }
}`,...(g=(f=a.parameters)==null?void 0:f.docs)==null?void 0:g.source}}};const T=["SlimTransparent","SlimFilled","SlimFilledBorderless","BoldFilled"];export{a as BoldFilled,r as SlimFilled,s as SlimFilledBorderless,e as SlimTransparent,T as __namedExportsOrder,y as default};
