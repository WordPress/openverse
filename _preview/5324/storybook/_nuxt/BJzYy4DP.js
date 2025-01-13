import{W as v}from"./CEIUB3th.js";import"./BQ2uyTwE.js";import{h as x}from"./ueSFnAt6.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="891af9d8-c670-4a0a-8e8a-ffe1347c3a66",e._sentryDebugIdIdentifier="sentry-dbid-891af9d8-c670-4a0a-8e8a-ffe1347c3a66")}catch{}})();const w={title:"Meta/Focus",decorators:[v]},d=e=>r=>({setup(){return()=>x("div",{class:`h-30 w-30 flex items-center justify-center ${e} ${r.classNames.join(" ")}`,"data-testid":"focus-target",tabindex:"0"},"Focus on me")}}),s={render:d("border border-disabled hover:border-hover").bind({}),name:"Slim transparent",args:{classNames:["focus-visible:focus-slim-tx"]}},a={render:d("bg-tertiary text-over-dark border border-tx").bind({}),name:"Slim filled",args:{classNames:["focus-slim-filled"]}},o={render:d("bg-primary text-over-dark").bind({}),name:"Slim filled borderless",args:{classNames:["focus-slim-borderless-filled"]}},l={render:d("bg-complementary text-default").bind({}),name:"Bold filled",args:{classNames:["focus-visible:focus-bold-filled"]}};var t,n,i;s.parameters={...s.parameters,docs:{...(t=s.parameters)==null?void 0:t.docs,source:{originalSource:`{
  render: GetTemplate("border border-disabled hover:border-hover").bind({}),
  name: "Slim transparent",
  args: {
    classNames: ["focus-visible:focus-slim-tx"]
  }
}`,...(i=(n=s.parameters)==null?void 0:n.docs)==null?void 0:i.source}}};var c,m,f;a.parameters={...a.parameters,docs:{...(c=a.parameters)==null?void 0:c.docs,source:{originalSource:`{
  render: GetTemplate("bg-tertiary text-over-dark border border-tx").bind({}),
  name: "Slim filled",
  args: {
    classNames: ["focus-slim-filled"]
  }
}`,...(f=(m=a.parameters)==null?void 0:m.docs)==null?void 0:f.source}}};var b,u,p;o.parameters={...o.parameters,docs:{...(b=o.parameters)==null?void 0:b.docs,source:{originalSource:`{
  render: GetTemplate("bg-primary text-over-dark").bind({}),
  name: "Slim filled borderless",
  args: {
    classNames: ["focus-slim-borderless-filled"]
  }
}`,...(p=(u=o.parameters)==null?void 0:u.docs)==null?void 0:p.source}}};var g,S,y;l.parameters={...l.parameters,docs:{...(g=l.parameters)==null?void 0:g.docs,source:{originalSource:`{
  render: GetTemplate("bg-complementary text-default").bind({}),
  name: "Bold filled",
  args: {
    classNames: ["focus-visible:focus-bold-filled"]
  }
}`,...(y=(S=l.parameters)==null?void 0:S.docs)==null?void 0:y.source}}};const B=["SlimTransparent","SlimFilled","SlimFilledBorderless","BoldFilled"];export{l as BoldFilled,a as SlimFilled,o as SlimFilledBorderless,s as SlimTransparent,B as __namedExportsOrder,w as default};
