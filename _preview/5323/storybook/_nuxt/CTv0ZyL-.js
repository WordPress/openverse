import{h as t}from"./DwwldUEF.js";import{_ as n}from"./mv8pzCEB.js";import"./_APRZIM1.js";import"./CpkulIne.js";import"./B6xXmqkp.js";import"./BNZBDzqs.js";import"./CVIvqSzo.js";import"./hEU2uDsT.js";import"./DbbxtPJM.js";import"./BAbDw2j1.js";import"./Ck0CgHQL.js";import"./Chgn5vcY.js";import"./DfKQSGJ_.js";import"./HE8VvABB.js";import"./BZyg411k.js";import"./--8yokH5.js";import"./D2_E7_fN.js";import"./BcTEa7d-.js";import"./zgpsPOGm.js";import"./DzAq6MI-.js";import"./CZGWR9g8.js";import"./D197vL4o.js";import"./DS5pDSwp.js";import"./5Ry8iPjm.js";import"./Dy2lpsBJ.js";import"./Dv6gP7wZ.js";import"./erT4Ktbo.js";import"./zDkj65pD.js";import"./DhTbjJlp.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="6551fb5f-a96f-4aad-afe3-31774e0e898d",e._sentryDebugIdIdentifier="sentry-dbid-6551fb5f-a96f-4aad-afe3-31774e0e898d")}catch{}})();const T={mediaType:{options:["audio","image"],control:{type:"radio"}},searchTerm:{control:{type:"string"}},resultsCount:{control:{type:"number"}},isSelected:{control:{type:"boolean"}},layout:{options:["stacked","horizontal"],control:{type:"radio"}}},W={title:"Components/VContentLink",component:n,argTypes:T},o={render:e=>({components:{VContentLink:n},setup(){return()=>t(n,e)}}),name:"Default",args:{mediaType:"image",searchTerm:"cat",resultsCount:5708}},a={name:"Horizontal",render:e=>({components:{VContentLink:n},setup(){return()=>t("div",{class:"max-w-md"},[t(n,e)])}}),args:{mediaType:"audio",searchTerm:"cat",resultsCount:4561,layout:"horizontal"}},s={render:()=>({components:{VContentLink:n},setup(){const e=[{mediaType:"image",resultsCount:4321},{mediaType:"audio",resultsCount:1234}];return()=>t("div",{class:"max-w-md mb-4 mt-2 grid grid-cols-2 gap-4 md:mt-0"},e.map(({mediaType:r,resultsCount:i},C)=>t(n,{mediaType:r,resultsCount:i,searchTerm:"cat",key:C})))}}),name:"Mobile",parameters:{viewport:{defaultViewport:"xs"}}};var m,p,d;o.parameters={...o.parameters,docs:{...(m=o.parameters)==null?void 0:m.docs,source:{originalSource:`{
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
}`,...(d=(p=o.parameters)==null?void 0:p.docs)==null?void 0:d.source}}};var u,c,l;a.parameters={...a.parameters,docs:{...(u=a.parameters)==null?void 0:u.docs,source:{originalSource:`{
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
}`,...(l=(c=a.parameters)==null?void 0:c.docs)==null?void 0:l.source}}};var y,g,f;s.parameters={...s.parameters,docs:{...(y=s.parameters)==null?void 0:y.docs,source:{originalSource:`{
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
}`,...(f=(g=s.parameters)==null?void 0:g.docs)==null?void 0:f.source}}};const X=["Default","Horizontal","Mobile"];export{o as Default,a as Horizontal,s as Mobile,X as __namedExportsOrder,W as default};
