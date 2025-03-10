import{h as t,d as m}from"./53SD24Bo.js";import{_ as a}from"./fW-bstkU.js";import{_ as n,V as s}from"./CYxeF2X6.js";import"./RQxsyxdU.js";import"./Duw_lVTV.js";import"./CxzE6WfI.js";import"./BsOxdBIg.js";import"./C4QhmNcb.js";import"./DhTbjJlp.js";import"./DYa50zxq.js";import"./ByZ6H8Q9.js";import"./oAL5f6fw.js";import"./Cai0IfA4.js";import"./B7ZxQ_gM.js";import"./CGdESDy3.js";import"./BALwooav.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},i=new e.Error().stack;i&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[i]="e46c74cd-46b1-448d-97e6-898ca993ed79",e._sentryDebugIdIdentifier="sentry-dbid-e46c74cd-46b1-448d-97e6-898ca993ed79")}catch{}})();const l=m({name:"VFilterTabWrapper",props:{appliedFilterCount:{type:Number,required:!0},selectedId:{type:String,required:!0}},setup(e){return()=>t("div",{class:"p-2"},[t(n,{label:"tabs",selectedId:e.selectedId,id:"wrapper",variant:"plain",tablistStyle:"ps-6 pe-2 gap-x-4",class:"flex min-h-0"},{tabs:()=>[t(s,{id:"tab1",label:"Tab 1",size:"medium"},{default:()=>["Tab1"]}),t(a,{appliedFilterCount:e.appliedFilterCount})]}),t("div",{class:"border-t border-default h-2 w-full"})])}}),W={title:"Components/VHeader/VHeaderMobile/VFilterTab",component:l,subcomponents:{VFilterTab:a,VTabs:n,VTab:s},argTypes:{appliedFilterCount:{type:"number"},selectedId:{control:"select",options:["filters","tab1"]}},args:{appliedFilterCount:3,selectedId:"filters"}},r={render:e=>({components:{VFilterTab:a,VTabs:n,VTab:s},setup(){return()=>t(l,{...e},{})}})};var o,p,d;r.parameters={...r.parameters,docs:{...(o=r.parameters)==null?void 0:o.docs,source:{originalSource:`{
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
