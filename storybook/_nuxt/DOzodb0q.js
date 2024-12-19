import{_ as a}from"./DkbcqcxL.js";import{_ as n,V as s}from"./BDZ8i9hs.js";import"./CDFarRZf.js";import{h as t,d as b}from"./Bf-AzR54.js";import"./C3jIBBvf.js";import"./HitohTq8.js";import"./8vSlX9Dy.js";import"./Big7CaLo.js";import"./DhTbjJlp.js";import"./C49ubYrZ.js";import"./G-2gs7Wx.js";import"./Xl6n5ahl.js";import"./DP0Qqza0.js";import"./CADoQZ_l.js";import"./nHVt-A68.js";import"./bYPJlIeP.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},i=new e.Error().stack;i&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[i]="20ddd680-4a5b-4bf5-b1d6-cdd946790cea",e._sentryDebugIdIdentifier="sentry-dbid-20ddd680-4a5b-4bf5-b1d6-cdd946790cea")}catch{}})();const l=b({name:"VFilterTabWrapper",props:{appliedFilterCount:{type:Number,required:!0},selectedId:{type:String,required:!0}},setup(e){return()=>t("div",{class:"p-2"},[t(n,{label:"tabs",selectedId:e.selectedId,id:"wrapper",variant:"plain",tablistStyle:"ps-6 pe-2 gap-x-4",class:"flex min-h-0"},{tabs:()=>[t(s,{id:"tab1",label:"Tab 1",size:"medium"},{default:()=>["Tab1"]}),t(a,{appliedFilterCount:e.appliedFilterCount})]}),t("div",{class:"border-t border-default h-2 w-full"})])}}),W={title:"Components/VHeader/VHeaderMobile/VFilterTab",component:l,subcomponents:{VFilterTab:a,VTabs:n,VTab:s},argTypes:{appliedFilterCount:{type:"number"},selectedId:{control:"select",options:["filters","tab1"]}},args:{appliedFilterCount:3,selectedId:"filters"}},r={render:e=>({components:{VFilterTab:a,VTabs:n,VTab:s},setup(){return()=>t(l,{...e},{})}})};var o,d,p;r.parameters={...r.parameters,docs:{...(o=r.parameters)==null?void 0:o.docs,source:{originalSource:`{
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
