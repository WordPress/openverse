import{_ as a}from"./CLWY20cp.js";import{_ as n,V as s}from"./B0b92HrV.js";import"./BQ2uyTwE.js";import{h as t,d as b}from"./ueSFnAt6.js";import"./DqwLVH-w.js";import"./CFNrPCvG.js";import"./B_AFY9SJ.js";import"./DDGXuWLI.js";import"./DhTbjJlp.js";import"./BOH1sSDC.js";import"./DKvPnfU5.js";import"./DI2Xpw6B.js";import"./DSEYgdJX.js";import"./A1b6Lb8y.js";import"./BQNGXNMh.js";import"./C4YS0AQy.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},i=new e.Error().stack;i&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[i]="f8f0b7ea-38b3-4891-a411-546f05c862b9",e._sentryDebugIdIdentifier="sentry-dbid-f8f0b7ea-38b3-4891-a411-546f05c862b9")}catch{}})();const l=b({name:"VFilterTabWrapper",props:{appliedFilterCount:{type:Number,required:!0},selectedId:{type:String,required:!0}},setup(e){return()=>t("div",{class:"p-2"},[t(n,{label:"tabs",selectedId:e.selectedId,id:"wrapper",variant:"plain",tablistStyle:"ps-6 pe-2 gap-x-4",class:"flex min-h-0"},{tabs:()=>[t(s,{id:"tab1",label:"Tab 1",size:"medium"},{default:()=>["Tab1"]}),t(a,{appliedFilterCount:e.appliedFilterCount})]}),t("div",{class:"border-t border-default h-2 w-full"})])}}),W={title:"Components/VHeader/VHeaderMobile/VFilterTab",component:l,subcomponents:{VFilterTab:a,VTabs:n,VTab:s},argTypes:{appliedFilterCount:{type:"number"},selectedId:{control:"select",options:["filters","tab1"]}},args:{appliedFilterCount:3,selectedId:"filters"}},r={render:e=>({components:{VFilterTab:a,VTabs:n,VTab:s},setup(){return()=>t(l,{...e},{})}})};var o,p,d;r.parameters={...r.parameters,docs:{...(o=r.parameters)==null?void 0:o.docs,source:{originalSource:`{
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
}`,...(d=(p=r.parameters)==null?void 0:p.docs)==null?void 0:d.source}}};const q=["Default"];export{r as Default,q as __namedExportsOrder,W as default};
