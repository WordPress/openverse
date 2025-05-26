import{i as t}from"./CKyfelsH.js";import{g as u}from"./BFequpbb.js";import{V as n,g as m}from"./DhmiD3Ot.js";import{u as f}from"./ETC5RdxK.js";import{_ as l}from"./qRoWk2aK.js";import{u as g}from"./B9Cuo1Ro.js";import"./ey6Ec0eW.js";import"./CD1OwZH3.js";import"./Bcilh3GR.js";import"./53SD24Bo.js";import"./D8YLUWro.js";import"./CzMus7W4.js";import"./B_xeuOb0.js";import"./DhVXE6x0.js";import"./okj3qyDJ.js";import"./Cw5DoNPI.js";import"./Bdn_xeD6.js";import"./B7QaUHa9.js";import"./C81jPTEF.js";import"./CCSsdpEp.js";import"./BxMTa-Rq.js";import"./DhTbjJlp.js";import"./CtCLusXQ.js";import"./V_R3UgdV.js";import"./hoiiP6gd.js";import"./DtcCBiui.js";import"./DzXFAWuk.js";import"./D6STwiFZ.js";import"./BPJprfCJ.js";import"./BQrorSEU.js";import"./B06vE1PI.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="03fc55bd-87e9-45de-91c6-65720b2909c5",e._sentryDebugIdIdentifier="sentry-dbid-03fc55bd-87e9-45de-91c6-65720b2909c5")}catch{}})();const a=u({originalTitle:"Test Audio",sensitivity:[],isSensitive:!1}),b={render:e=>({template:`
    <div class="flex flex-col gap-y-2">
      <VLanguageSelect />
      <section class="wrapper flex flex-col p-2 gap-y-2 bg-surface">
        <VMetadata
        v-for="datum in data"
        :key="datum.media.id"
        :metadata="datum.metadata"
        :media="datum.media"
        v-bind="datum"
        class="bg-default"/>
      </section>
    </div>
  `,components:{VMetadata:n,VLanguageSelect:l},setup(){f().$patch({providers:{audio:[{source_name:a.source}],image:[{source_name:t.source}]},sourceNames:{audio:[a.source],image:[t.source]}});const{t:i}=g({useScope:"global"}),c=[{metadata:m(t,i,{width:t.width,height:t.height,type:t.filetype}),media:t},{metadata:m(a,i),media:a}];return{args:e,data:c}}})},U={title:"Components/VMediaInfo/VMetadata",component:n},o={...b,name:"VMetadata"};var s,d,p;o.parameters={...o.parameters,docs:{...(s=o.parameters)==null?void 0:s.docs,source:{originalSource:`{
  ...Template,
  name: "VMetadata"
}`,...(p=(d=o.parameters)==null?void 0:d.docs)==null?void 0:p.source}}};const W=["Default"];export{o as Default,W as __namedExportsOrder,U as default};
