import{_ as e}from"./Djsbot0x.js";import{h as t}from"./lnpB3OcH.js";import"./BNurbrIm.js";import"./TZ8H9kUZ.js";import"./ONOUNYGt.js";import"./CRWjC3CT.js";import"./BJ-KpVIG.js";import"./BInFDkJi.js";import"./BvLt3-_D.js";import"./CFMQYC2y.js";import"./Dt-H8hG_.js";import"./CTON8dBl.js";import"./CoPWYLvr.js";import"./Cpj98o6Y.js";import"./Ci7G4jyV.js";import"./PgLs4BFy.js";import"./D0ww02ZN.js";import"./wqDFrKMd.js";import"./DToSwJe0.js";import"./CVtkxrq9.js";import"./Xs_VBmP5.js";import"./DinEHs6j.js";import"./B-JuYQep.js";import"./BVzzViWI.js";import"./DuVMw8T-.js";import"./BOX21o1p.js";import"./CtE17snF.js";import"./D-c0xjtQ.js";import"./ZjNmaQpL.js";import"./CuPsdpTl.js";import"./DlAUqK2U.js";const h={mediaType:{options:["audio","image"],control:{type:"radio"}},searchTerm:{control:{type:"string"}},resultsCount:{control:{type:"number"}},isSelected:{control:{type:"boolean"}},layout:{options:["stacked","horizontal"],control:{type:"radio"}}},X={title:"Components/VContentLink",component:e,argTypes:h},r={render:n=>({components:{VContentLink:e},setup(){return()=>t(e,n)}}),name:"Default",args:{mediaType:"image",searchTerm:"cat",resultsCount:5708}},o={name:"Horizontal",render:n=>({components:{VContentLink:e},setup(){return()=>t("div",{class:"max-w-md"},[t(e,n)])}}),args:{mediaType:"audio",searchTerm:"cat",resultsCount:4561,layout:"horizontal"}},a={render:()=>({components:{VContentLink:e},setup(){const n=[{mediaType:"image",resultsCount:4321},{mediaType:"audio",resultsCount:1234}];return()=>t("div",{class:"max-w-md mb-4 mt-2 grid grid-cols-2 gap-4 md:mt-0"},n.map(({mediaType:g,resultsCount:C},T)=>t(e,{mediaType:g,resultsCount:C,searchTerm:"cat",key:T})))}}),name:"Mobile",parameters:{viewport:{defaultViewport:"xs"}}};var s,m,i;r.parameters={...r.parameters,docs:{...(s=r.parameters)==null?void 0:s.docs,source:{originalSource:`{
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
}`,...(i=(m=r.parameters)==null?void 0:m.docs)==null?void 0:i.source}}};var p,c,u;o.parameters={...o.parameters,docs:{...(p=o.parameters)==null?void 0:p.docs,source:{originalSource:`{
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
  args: ({
    mediaType: "audio",
    searchTerm: "cat",
    resultsCount: 4561,
    layout: "horizontal"
  } as typeof VContentLink.props)
}`,...(u=(c=o.parameters)==null?void 0:c.docs)==null?void 0:u.source}}};var d,l,y;a.parameters={...a.parameters,docs:{...(d=a.parameters)==null?void 0:d.docs,source:{originalSource:`{
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
        mediaType: (mediaType as SupportedMediaType),
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
}`,...(y=(l=a.parameters)==null?void 0:l.docs)==null?void 0:y.source}}};const Y=["Default","Horizontal","Mobile"];export{r as Default,o as Horizontal,a as Mobile,Y as __namedExportsOrder,X as default};
