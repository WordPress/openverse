import{_ as n}from"./ImjS-syG.js";import"./DJiKieMK.js";import{h as t}from"./Bf-AzR54.js";import"./D9JVarWf.js";import"./DPCAinxI.js";import"./DHc3v09i.js";import"./DIoPOIW-.js";import"./DP_WGbG6.js";import"./Bny5abkt.js";import"./HRLWcGUV.js";import"./BHCnpuXR.js";import"./B06Wl6je.js";import"./l54NnjUF.js";import"./CeH6ebnn.js";import"./DCDaOnb6.js";import"./C-dE80hk.js";import"./CUsr6PUM.js";import"./qA--S04K.js";import"./XhmO_eME.js";import"./tw9gWovy.js";import"./DzAq6MI-.js";import"./bqX4GSlx.js";import"./DJ89QBAT.js";import"./BG7tCcxx.js";import"./BtGsfS_x.js";import"./CdpvutFv.js";import"./Cyf2jyE0.js";import"./DcwCHNwG.js";import"./BgVAWI2R.js";import"./cGIRWP1M.js";import"./BAvHRt8K.js";import"./DhTbjJlp.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="0581e537-9e08-4547-8c7c-2926d83a52ce",e._sentryDebugIdIdentifier="sentry-dbid-0581e537-9e08-4547-8c7c-2926d83a52ce")}catch{}})();const f={mediaType:{options:["audio","image"],control:{type:"radio"}},searchTerm:{control:{type:"string"}},resultsCount:{control:{type:"number"}},isSelected:{control:{type:"boolean"}},layout:{options:["stacked","horizontal"],control:{type:"radio"}}},Z={title:"Components/VContentLink",component:n,argTypes:f},o={render:e=>({components:{VContentLink:n},setup(){return()=>t(n,e)}}),name:"Default",args:{mediaType:"image",searchTerm:"cat",resultsCount:5708}},a={name:"Horizontal",render:e=>({components:{VContentLink:n},setup(){return()=>t("div",{class:"max-w-md"},[t(n,e)])}}),args:{mediaType:"audio",searchTerm:"cat",resultsCount:4561,layout:"horizontal"}},s={render:()=>({components:{VContentLink:n},setup(){const e=[{mediaType:"image",resultsCount:4321},{mediaType:"audio",resultsCount:1234}];return()=>t("div",{class:"max-w-md mb-4 mt-2 grid grid-cols-2 gap-4 md:mt-0"},e.map(({mediaType:r,resultsCount:i},T)=>t(n,{mediaType:r,resultsCount:i,searchTerm:"cat",key:T})))}}),name:"Mobile",parameters:{viewport:{defaultViewport:"xs"}}};var m,p,d;o.parameters={...o.parameters,docs:{...(m=o.parameters)==null?void 0:m.docs,source:{originalSource:`{
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
