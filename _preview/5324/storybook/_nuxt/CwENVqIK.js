import{_ as n}from"./BDTAjGMz.js";import"./BQ2uyTwE.js";import{h as t}from"./ueSFnAt6.js";import"./dNCV0R31.js";import"./CpkgunxC.js";import"./BUcLuzj5.js";import"./BKvBQNfv.js";import"./BKGw6EjD.js";import"./D9PGBJDx.js";import"./CxIz9G_3.js";import"./DSEYgdJX.js";import"./cS2ccka-.js";import"./EYmIadoG.js";import"./nu0uObuU.js";import"./CP2tuLu8.js";import"./BXlC2Afm.js";import"./DHgysDkh.js";import"./C4YS0AQy.js";import"./5wCrcqN-.js";import"./C_jCWbT6.js";import"./DzAq6MI-.js";import"./D2P1fKwO.js";import"./KoGT8mmZ.js";import"./DlgfYiH5.js";import"./DKvPnfU5.js";import"./DI2Xpw6B.js";import"./A1b6Lb8y.js";import"./BQNGXNMh.js";import"./DDGXuWLI.js";import"./CFNrPCvG.js";import"./B_AFY9SJ.js";import"./DhTbjJlp.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="931f07b7-8316-4e40-a702-39face67bcf8",e._sentryDebugIdIdentifier="sentry-dbid-931f07b7-8316-4e40-a702-39face67bcf8")}catch{}})();const T={mediaType:{options:["audio","image"],control:{type:"radio"}},searchTerm:{control:{type:"string"}},resultsCount:{control:{type:"number"}},isSelected:{control:{type:"boolean"}},layout:{options:["stacked","horizontal"],control:{type:"radio"}}},Z={title:"Components/VContentLink",component:n,argTypes:T},o={render:e=>({components:{VContentLink:n},setup(){return()=>t(n,e)}}),name:"Default",args:{mediaType:"image",searchTerm:"cat",resultsCount:5708}},a={name:"Horizontal",render:e=>({components:{VContentLink:n},setup(){return()=>t("div",{class:"max-w-md"},[t(n,e)])}}),args:{mediaType:"audio",searchTerm:"cat",resultsCount:4561,layout:"horizontal"}},s={render:()=>({components:{VContentLink:n},setup(){const e=[{mediaType:"image",resultsCount:4321},{mediaType:"audio",resultsCount:1234}];return()=>t("div",{class:"max-w-md mb-4 mt-2 grid grid-cols-2 gap-4 md:mt-0"},e.map(({mediaType:r,resultsCount:i},C)=>t(n,{mediaType:r,resultsCount:i,searchTerm:"cat",key:C})))}}),name:"Mobile",parameters:{viewport:{defaultViewport:"xs"}}};var m,p,d;o.parameters={...o.parameters,docs:{...(m=o.parameters)==null?void 0:m.docs,source:{originalSource:`{
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
}`,...(l=(u=a.parameters)==null?void 0:u.docs)==null?void 0:l.source}}};var y,g,f;s.parameters={...s.parameters,docs:{...(y=s.parameters)==null?void 0:y.docs,source:{originalSource:`{
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
}`,...(f=(g=s.parameters)==null?void 0:g.docs)==null?void 0:f.source}}};const $=["Default","Horizontal","Mobile"];export{o as Default,a as Horizontal,s as Mobile,$ as __namedExportsOrder,Z as default};
