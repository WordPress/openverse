import{h as t}from"./DwwldUEF.js";import{_ as n}from"./CM7JFGhQ.js";import"./BKd6qjwJ.js";import"./CMdMEjwX.js";import"./DyjmqLvs.js";import"./DyntKXIc.js";import"./B_JavP0r.js";import"./TJSYFxys.js";import"./DXt3Hw-9.js";import"./DrQM85Nc.js";import"./Ck0CgHQL.js";import"./DeIUwsAH.js";import"./Bc_6hboB.js";import"./BJKkpTjt.js";import"./DIa_evZO.js";import"./D5nIdk7e.js";import"./DEzOOYTC.js";import"./BA2RD0IG.js";import"./BwtrEtqR.js";import"./DzAq6MI-.js";import"./BYD-UmPb.js";import"./DVxzvkhI.js";import"./maH52C8u.js";import"./R_--_Flr.js";import"./Duzn9Bak.js";import"./B7G-YaxP.js";import"./Efi66Qad.js";import"./DjJGxhuO.js";import"./D318SDY2.js";import"./BMyQprRt.js";import"./DhTbjJlp.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="2be5998d-2330-43bb-ae44-7deacc47fa10",e._sentryDebugIdIdentifier="sentry-dbid-2be5998d-2330-43bb-ae44-7deacc47fa10")}catch{}})();const T={mediaType:{options:["audio","image"],control:{type:"radio"}},searchTerm:{control:{type:"string"}},resultsCount:{control:{type:"number"}},isSelected:{control:{type:"boolean"}},layout:{options:["stacked","horizontal"],control:{type:"radio"}}},Y={title:"Components/VContentLink",component:n,argTypes:T},o={render:e=>({components:{VContentLink:n},setup(){return()=>t(n,e)}}),name:"Default",args:{mediaType:"image",searchTerm:"cat",resultsCount:5708}},a={name:"Horizontal",render:e=>({components:{VContentLink:n},setup(){return()=>t("div",{class:"max-w-md"},[t(n,e)])}}),args:{mediaType:"audio",searchTerm:"cat",resultsCount:4561,layout:"horizontal"}},s={render:()=>({components:{VContentLink:n},setup(){const e=[{mediaType:"image",resultsCount:4321},{mediaType:"audio",resultsCount:1234}];return()=>t("div",{class:"max-w-md mb-4 mt-2 grid grid-cols-2 gap-4 md:mt-0"},e.map(({mediaType:r,resultsCount:i},C)=>t(n,{mediaType:r,resultsCount:i,searchTerm:"cat",key:C})))}}),name:"Mobile",parameters:{viewport:{defaultViewport:"xs"}}};var m,p,d;o.parameters={...o.parameters,docs:{...(m=o.parameters)==null?void 0:m.docs,source:{originalSource:`{
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
}`,...(f=(g=s.parameters)==null?void 0:g.docs)==null?void 0:f.source}}};const Z=["Default","Horizontal","Mobile"];export{o as Default,a as Horizontal,s as Mobile,Z as __namedExportsOrder,Y as default};
