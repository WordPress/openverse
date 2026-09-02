import{i as t}from"./BtEMBbZq.js";import{g as u}from"./Dq4kkPaf.js";import{V as n,g as m}from"./BGVzvPV6.js";import{u as f}from"./CNOfB5vH.js";import{_ as l}from"./TrS39Ew9.js";import{u as g}from"./B9Cuo1Ro.js";import"./DSrDAhJH.js";import"./D9Az8HPp.js";import"./Cz1YM6_r.js";import"./53SD24Bo.js";import"./iy3krge0.js";import"./BVoU5gzH.js";import"./e2yY43HP.js";import"./9xj2VA-m.js";import"./okj3qyDJ.js";import"./DW11D-YO.js";import"./ProZPLPW.js";import"./Dkz41V7r.js";import"./BWKbF-QS.js";import"./Cpe-Oxin.js";import"./CGiaWBvD.js";import"./DhTbjJlp.js";import"./DncsuqBF.js";import"./BAGVCeL6.js";import"./Bzg618fq.js";import"./DaaoxyFL.js";import"./B65OKO0j.js";import"./h1cGCrsl.js";import"./BsvyKpHN.js";import"./BQrorSEU.js";import"./B06vE1PI.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="03fc55bd-87e9-45de-91c6-65720b2909c5",e._sentryDebugIdIdentifier="sentry-dbid-03fc55bd-87e9-45de-91c6-65720b2909c5")}catch{}})();const a=u({originalTitle:"Test Audio",sensitivity:[],isSensitive:!1}),b={render:e=>({template:`
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
