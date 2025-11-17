import{h as v}from"./DwwldUEF.js";import{W as x}from"./r7DnlIPq.js";import"./CWoQmekT.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="389ccd83-d58c-40aa-909a-e12543faccc6",e._sentryDebugIdIdentifier="sentry-dbid-389ccd83-d58c-40aa-909a-e12543faccc6")}catch{}})();const w={title:"Meta/Focus",decorators:[x]},l=e=>r=>({setup(){return()=>v("div",{class:`h-30 w-30 flex items-center justify-center ${e} ${r.classNames.join(" ")}`,"data-testid":"focus-target",tabindex:"0"},"Focus on me")}}),s={render:l("border border-disabled hover:border-hover").bind({}),name:"Slim transparent",args:{classNames:["focus-visible:focus-slim-tx"]}},a={render:l("bg-tertiary text-over-dark border border-tx").bind({}),name:"Slim filled",args:{classNames:["focus-slim-filled"]}},o={render:l("bg-primary text-over-dark").bind({}),name:"Slim filled borderless",args:{classNames:["focus-slim-borderless-filled"]}},d={render:l("bg-complementary text-default").bind({}),name:"Bold filled",args:{classNames:["focus-visible:focus-bold-filled"]}};var t,n,i;s.parameters={...s.parameters,docs:{...(t=s.parameters)==null?void 0:t.docs,source:{originalSource:`{
  render: GetTemplate("border border-disabled hover:border-hover").bind({}),
  name: "Slim transparent",
  args: {
    classNames: ["focus-visible:focus-slim-tx"]
  }
}`,...(i=(n=s.parameters)==null?void 0:n.docs)==null?void 0:i.source}}};var c,m,b;a.parameters={...a.parameters,docs:{...(c=a.parameters)==null?void 0:c.docs,source:{originalSource:`{
  render: GetTemplate("bg-tertiary text-over-dark border border-tx").bind({}),
  name: "Slim filled",
  args: {
    classNames: ["focus-slim-filled"]
  }
}`,...(b=(m=a.parameters)==null?void 0:m.docs)==null?void 0:b.source}}};var f,u,p;o.parameters={...o.parameters,docs:{...(f=o.parameters)==null?void 0:f.docs,source:{originalSource:`{
  render: GetTemplate("bg-primary text-over-dark").bind({}),
  name: "Slim filled borderless",
  args: {
    classNames: ["focus-slim-borderless-filled"]
  }
}`,...(p=(u=o.parameters)==null?void 0:u.docs)==null?void 0:p.source}}};var g,S,y;d.parameters={...d.parameters,docs:{...(g=d.parameters)==null?void 0:g.docs,source:{originalSource:`{
  render: GetTemplate("bg-complementary text-default").bind({}),
  name: "Bold filled",
  args: {
    classNames: ["focus-visible:focus-bold-filled"]
  }
}`,...(y=(S=d.parameters)==null?void 0:S.docs)==null?void 0:y.source}}};const B=["SlimTransparent","SlimFilled","SlimFilledBorderless","BoldFilled"];export{d as BoldFilled,a as SlimFilled,o as SlimFilledBorderless,s as SlimTransparent,B as __namedExportsOrder,w as default};
