import{_ as a}from"./PRNjm3cr.js";import{_ as n,V as s}from"./xRu-1gDA.js";import"./DHOw7aFH.js";import{h as t,d as b}from"./Bf-AzR54.js";import"./D3k92WPk.js";import"./lASKgZAk.js";import"./DnikNTKn.js";import"./DMScrd9r.js";import"./DhTbjJlp.js";import"./DZQPxovG.js";import"./DG5kPZbt.js";import"./CTiRmcG7.js";import"./Btoo3kXe.js";import"./Btjq2moo.js";import"./rdZXP2j6.js";import"./BUZMDrXj.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},i=new e.Error().stack;i&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[i]="20ddd680-4a5b-4bf5-b1d6-cdd946790cea",e._sentryDebugIdIdentifier="sentry-dbid-20ddd680-4a5b-4bf5-b1d6-cdd946790cea")}catch{}})();const l=b({name:"VFilterTabWrapper",props:{appliedFilterCount:{type:Number,required:!0},selectedId:{type:String,required:!0}},setup(e){return()=>t("div",{class:"p-2"},[t(n,{label:"tabs",selectedId:e.selectedId,id:"wrapper",variant:"plain",tablistStyle:"ps-6 pe-2 gap-x-4",class:"flex min-h-0"},{tabs:()=>[t(s,{id:"tab1",label:"Tab 1",size:"medium"},{default:()=>["Tab1"]}),t(a,{appliedFilterCount:e.appliedFilterCount})]}),t("div",{class:"border-t border-default h-2 w-full"})])}}),W={title:"Components/VHeader/VHeaderMobile/VFilterTab",component:l,subcomponents:{VFilterTab:a,VTabs:n,VTab:s},argTypes:{appliedFilterCount:{type:"number"},selectedId:{control:"select",options:["filters","tab1"]}},args:{appliedFilterCount:3,selectedId:"filters"}},r={render:e=>({components:{VFilterTab:a,VTabs:n,VTab:s},setup(){return()=>t(l,{...e},{})}})};var o,d,p;r.parameters={...r.parameters,docs:{...(o=r.parameters)==null?void 0:o.docs,source:{originalSource:`{
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
