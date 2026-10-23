import{h as t,d as b}from"./DmrXErv4.js";import{_ as a}from"./BOi8xoLO.js";import{V as n,_ as i}from"./C2cy-l62.js";import"./Cre_5D1H.js";import"./DMHhTBZb.js";import"./rMKLwKwR.js";import"./Dv0Nl23j.js";import"./Bn7RUpRV.js";import"./DhTbjJlp.js";import"./CDE4LuQ1.js";import"./BRHrr7ck.js";import"./Bpr67t9y.js";import"./B3KNKrKa.js";import"./DWRfakdt.js";import"./CCN4kZnP.js";import"./B_dsH32H.js";import"./OMXwMIS8.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},o=new e.Error().stack;o&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[o]="c30ac17f-c44b-4525-93b7-316bfa13b868",e._sentryDebugIdIdentifier="sentry-dbid-c30ac17f-c44b-4525-93b7-316bfa13b868")}catch{}})();const l=b({name:"VFilterTabWrapper",props:{appliedFilterCount:{type:Number,required:!0},selectedId:{type:String,required:!0}},setup(e){return()=>t("div",{class:"p-2"},[t(i,{label:"tabs",selectedId:e.selectedId,id:"wrapper",variant:"plain",tablistStyle:"ps-6 pe-2 gap-x-4",class:"flex min-h-0"},{tabs:()=>[t(n,{id:"tab1",label:"Tab 1",size:"medium"},{default:()=>["Tab1"]}),t(a,{appliedFilterCount:e.appliedFilterCount})]}),t("div",{class:"border-t border-default h-2 w-full"})])}}),q={title:"Components/VHeader/VHeaderMobile/VFilterTab",component:l,subcomponents:{VFilterTab:a,VTabs:i,VTab:n},argTypes:{appliedFilterCount:{type:"number"},selectedId:{control:"select",options:["filters","tab1"]}},args:{appliedFilterCount:3,selectedId:"filters"}},r={render:e=>({components:{VFilterTab:a,VTabs:i,VTab:n},setup(){return()=>t(l,{...e},{})}})};var s,p,d;r.parameters={...r.parameters,docs:{...(s=r.parameters)==null?void 0:s.docs,source:{originalSource:`{
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
}`,...(d=(p=r.parameters)==null?void 0:p.docs)==null?void 0:d.source}}};const E=["Default"];export{r as Default,E as __namedExportsOrder,q as default};
