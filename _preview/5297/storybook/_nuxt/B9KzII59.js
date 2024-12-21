import{_ as n}from"./oiEGLxIm.js";import"./D6xGyQxu.js";import{h as t}from"./Bf-AzR54.js";import"./D9JVarWf.js";import"./nYjMtbHY.js";import"./CkK3diBk.js";import"./BxCgZ025.js";import"./BnJZTjE_.js";import"./CUyQTIYr.js";import"./BsG3jt0b.js";import"./CRElLIkf.js";import"./B06Wl6je.js";import"./C7lp-ITr.js";import"./BZTl3SGY.js";import"./SxvBqf-I.js";import"./BvQxCwAx.js";import"./Tu1w6jvB.js";import"./DBWmBUzF.js";import"./eAGCzEdq.js";import"./G0IPDLoE.js";import"./DzAq6MI-.js";import"./D2OdtNy-.js";import"./ChR6vGgT.js";import"./DgZsT532.js";import"./6ItBZc85.js";import"./v8hTCxed.js";import"./D3fY7LA9.js";import"./EvZx83Uz.js";import"./p8nc5Li4.js";import"./DmNhhvCU.js";import"./CO4aZKIX.js";import"./DhTbjJlp.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="0581e537-9e08-4547-8c7c-2926d83a52ce",e._sentryDebugIdIdentifier="sentry-dbid-0581e537-9e08-4547-8c7c-2926d83a52ce")}catch{}})();const f={mediaType:{options:["audio","image"],control:{type:"radio"}},searchTerm:{control:{type:"string"}},resultsCount:{control:{type:"number"}},isSelected:{control:{type:"boolean"}},layout:{options:["stacked","horizontal"],control:{type:"radio"}}},Z={title:"Components/VContentLink",component:n,argTypes:f},o={render:e=>({components:{VContentLink:n},setup(){return()=>t(n,e)}}),name:"Default",args:{mediaType:"image",searchTerm:"cat",resultsCount:5708}},a={name:"Horizontal",render:e=>({components:{VContentLink:n},setup(){return()=>t("div",{class:"max-w-md"},[t(n,e)])}}),args:{mediaType:"audio",searchTerm:"cat",resultsCount:4561,layout:"horizontal"}},s={render:()=>({components:{VContentLink:n},setup(){const e=[{mediaType:"image",resultsCount:4321},{mediaType:"audio",resultsCount:1234}];return()=>t("div",{class:"max-w-md mb-4 mt-2 grid grid-cols-2 gap-4 md:mt-0"},e.map(({mediaType:r,resultsCount:i},T)=>t(n,{mediaType:r,resultsCount:i,searchTerm:"cat",key:T})))}}),name:"Mobile",parameters:{viewport:{defaultViewport:"xs"}}};var m,p,d;o.parameters={...o.parameters,docs:{...(m=o.parameters)==null?void 0:m.docs,source:{originalSource:`{
  render: args => ({
    components: {
      VContentLink
    },
    setup() {
      return () => h(VContentLink, args);
    }
  }),
  name: "Default",
  args: {
    mediaType: "image",
    searchTerm: "cat",
    resultsCount: 5708
  }
}`,...(d=(p=o.parameters)==null?void 0:p.docs)==null?void 0:d.source}}};var c,u,l;a.parameters={...a.parameters,docs:{...(c=a.parameters)==null?void 0:c.docs,source:{originalSource:`{
  name: "Horizontal",
  render: args => ({
    components: {
      VContentLink
    },
    setup() {
      return () => h("div", {
        class: "max-w-md"
      }, [h(VContentLink, args)]);
    }
  }),
  args: {
    mediaType: "audio",
    searchTerm: "cat",
    resultsCount: 4561,
    layout: "horizontal"
  } as typeof VContentLink.props
}`,...(l=(u=a.parameters)==null?void 0:u.docs)==null?void 0:l.source}}};var y,g,C;s.parameters={...s.parameters,docs:{...(y=s.parameters)==null?void 0:y.docs,source:{originalSource:`{
  render: () => ({
    components: {
      VContentLink
    },
    setup() {
      const types = [{
        mediaType: "image",
        resultsCount: 4321
      }, {
        mediaType: "audio",
        resultsCount: 1234
      }];
      return () => h("div", {
        class: "max-w-md mb-4 mt-2 grid grid-cols-2 gap-4 md:mt-0"
      }, types.map(({
        mediaType,
        resultsCount
      }, key) => h(VContentLink, {
        mediaType: mediaType as SupportedMediaType,
        resultsCount,
        searchTerm: "cat",
        key
      })));
    }
  }),
  name: "Mobile",
  parameters: {
    viewport: {
      defaultViewport: "xs"
    }
  }
}`,...(C=(g=s.parameters)==null?void 0:g.docs)==null?void 0:C.source}}};const $=["Default","Horizontal","Mobile"];export{o as Default,a as Horizontal,s as Mobile,$ as __namedExportsOrder,Z as default};
