import{h as t}from"./DwwldUEF.js";import{_ as n}from"./zZyMCmQJ.js";import"./CjQ0HQF0.js";import"./DdZobGJ0.js";import"./CFZbsX2Q.js";import"./Gc5ScyLZ.js";import"./C6VqcP4x.js";import"./Ley1esUq.js";import"./C0pA7UPR.js";import"./rq0rg1X-.js";import"./Ck0CgHQL.js";import"./CUsfujdM.js";import"./DmsD6orq.js";import"./BIohVJVH.js";import"./KlWK2kB1.js";import"./CD6Nr1ia.js";import"./BufT_yKp.js";import"./BuC5_mLh.js";import"./DcMSHMAp.js";import"./DzAq6MI-.js";import"./CTGRm2NM.js";import"./DyhVoU-3.js";import"./D7DxMZPa.js";import"./Bl4H7SX1.js";import"./DZZ1Fr_1.js";import"./B67cIdux.js";import"./Cqs9wCPQ.js";import"./D9b6d0V7.js";import"./Bu-vEs7l.js";import"./Dwl_h6Xz.js";import"./DhTbjJlp.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="2be5998d-2330-43bb-ae44-7deacc47fa10",e._sentryDebugIdIdentifier="sentry-dbid-2be5998d-2330-43bb-ae44-7deacc47fa10")}catch{}})();const T={mediaType:{options:["audio","image"],control:{type:"radio"}},searchTerm:{control:{type:"string"}},resultsCount:{control:{type:"number"}},isSelected:{control:{type:"boolean"}},layout:{options:["stacked","horizontal"],control:{type:"radio"}}},Y={title:"Components/VContentLink",component:n,argTypes:T},o={render:e=>({components:{VContentLink:n},setup(){return()=>t(n,e)}}),name:"Default",args:{mediaType:"image",searchTerm:"cat",resultsCount:5708}},a={name:"Horizontal",render:e=>({components:{VContentLink:n},setup(){return()=>t("div",{class:"max-w-md"},[t(n,e)])}}),args:{mediaType:"audio",searchTerm:"cat",resultsCount:4561,layout:"horizontal"}},s={render:()=>({components:{VContentLink:n},setup(){const e=[{mediaType:"image",resultsCount:4321},{mediaType:"audio",resultsCount:1234}];return()=>t("div",{class:"max-w-md mb-4 mt-2 grid grid-cols-2 gap-4 md:mt-0"},e.map(({mediaType:r,resultsCount:i},C)=>t(n,{mediaType:r,resultsCount:i,searchTerm:"cat",key:C})))}}),name:"Mobile",parameters:{viewport:{defaultViewport:"xs"}}};var m,p,d;o.parameters={...o.parameters,docs:{...(m=o.parameters)==null?void 0:m.docs,source:{originalSource:`{
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
