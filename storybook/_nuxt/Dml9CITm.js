import{h as t,d as m}from"./53SD24Bo.js";import{_ as a}from"./CFrfze0e.js";import{_ as n,V as i}from"./CsqVNwQU.js";import"./_bbq3c9C.js";import"./CZxAQxn1.js";import"./dvXbmdTd.js";import"./ivjvpZKc.js";import"./DjsporFN.js";import"./DhTbjJlp.js";import"./Dh8GjfY7.js";import"./DlboKt2a.js";import"./Di7dAt70.js";import"./B9k6C3Hw.js";import"./BOewZ2sR.js";import"./D2GrBf-6.js";import"./B_-6Taiq.js";import"./CH5-dTGy.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},o=new e.Error().stack;o&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[o]="252d358b-4667-4f74-ae4d-483d636cb8e3",e._sentryDebugIdIdentifier="sentry-dbid-252d358b-4667-4f74-ae4d-483d636cb8e3")}catch{}})();const l=m({name:"VFilterTabWrapper",props:{appliedFilterCount:{type:Number,required:!0},selectedId:{type:String,required:!0}},setup(e){return()=>t("div",{class:"p-2"},[t(n,{label:"tabs",selectedId:e.selectedId,id:"wrapper",variant:"plain",tablistStyle:"ps-6 pe-2 gap-x-4",class:"flex min-h-0"},{tabs:()=>[t(i,{id:"tab1",label:"Tab 1",size:"medium"},{default:()=>["Tab1"]}),t(a,{appliedFilterCount:e.appliedFilterCount})]}),t("div",{class:"border-t border-default h-2 w-full"})])}}),q={title:"Components/VHeader/VHeaderMobile/VFilterTab",component:l,subcomponents:{VFilterTab:a,VTabs:n,VTab:i},argTypes:{appliedFilterCount:{type:"number"},selectedId:{control:"select",options:["filters","tab1"]}},args:{appliedFilterCount:3,selectedId:"filters"}},r={render:e=>({components:{VFilterTab:a,VTabs:n,VTab:i},setup(){return()=>t(l,{...e},{})}})};var s,p,d;r.parameters={...r.parameters,docs:{...(s=r.parameters)==null?void 0:s.docs,source:{originalSource:`{
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
