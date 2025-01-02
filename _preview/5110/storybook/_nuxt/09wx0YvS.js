import{_ as a}from"./DauNV9j5.js";import{_ as n,V as s}from"./DmyJxl6r.js";import"./DUksCy1Q.js";import{h as t,d as b}from"./Bf-AzR54.js";import"./BtRzq8b5.js";import"./CAhZsXLM.js";import"./BEmSFkVT.js";import"./8Pdn1Bl1.js";import"./DhTbjJlp.js";import"./BgqWDxf_.js";import"./DIrLFUJi.js";import"./CGo6q8cg.js";import"./DekjSk5G.js";import"./Cf91XFr0.js";import"./CvkTs5vB.js";import"./CQEj5Ugn.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},i=new e.Error().stack;i&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[i]="20ddd680-4a5b-4bf5-b1d6-cdd946790cea",e._sentryDebugIdIdentifier="sentry-dbid-20ddd680-4a5b-4bf5-b1d6-cdd946790cea")}catch{}})();const l=b({name:"VFilterTabWrapper",props:{appliedFilterCount:{type:Number,required:!0},selectedId:{type:String,required:!0}},setup(e){return()=>t("div",{class:"p-2"},[t(n,{label:"tabs",selectedId:e.selectedId,id:"wrapper",variant:"plain",tablistStyle:"ps-6 pe-2 gap-x-4",class:"flex min-h-0"},{tabs:()=>[t(s,{id:"tab1",label:"Tab 1",size:"medium"},{default:()=>["Tab1"]}),t(a,{appliedFilterCount:e.appliedFilterCount})]}),t("div",{class:"border-t border-default h-2 w-full"})])}}),W={title:"Components/VHeader/VHeaderMobile/VFilterTab",component:l,subcomponents:{VFilterTab:a,VTabs:n,VTab:s},argTypes:{appliedFilterCount:{type:"number"},selectedId:{control:"select",options:["filters","tab1"]}},args:{appliedFilterCount:3,selectedId:"filters"}},r={render:e=>({components:{VFilterTab:a,VTabs:n,VTab:s},setup(){return()=>t(l,{...e},{})}})};var o,d,p;r.parameters={...r.parameters,docs:{...(o=r.parameters)==null?void 0:o.docs,source:{originalSource:`{
  render: args => ({
    components: {
      VFilterTab,
      VTabs,
      VTab
    },
    setup() {
      return () => h(VFilterTabWrapper, {
        ...args
      }, {});
    }
  })
}`,...(p=(d=r.parameters)==null?void 0:d.docs)==null?void 0:p.source}}};const q=["Default"];export{r as Default,q as __namedExportsOrder,W as default};
