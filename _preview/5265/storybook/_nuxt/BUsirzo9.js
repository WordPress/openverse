import{i as t}from"./ByODRZ_L.js";import{g as u}from"./cqDaMTDA.js";import{V as n,g as m}from"./DqAbNI4A.js";import{u as f}from"./D8qJDlnG.js";import{_ as l}from"./gRQEeVrp.js";import{u as g}from"./D93TPuWH.js";import"./CWoQmekT.js";import"./CAa63J2U.js";import"./Cyc9srVp.js";import"./DwwldUEF.js";import"./Bkc2CSET.js";import"./jkP_3ymO.js";import"./Z8zkSHZ1.js";import"./C8BbUAkk.js";import"./DzAq6MI-.js";import"./DqyB4W5h.js";import"./BtS8wA1z.js";import"./tAHCZdDM.js";import"./VcnMPoS3.js";import"./DoSYsHAz.js";import"./aezMCrU2.js";import"./DhTbjJlp.js";import"./DZP0BHtF.js";import"./PhiECvvt.js";import"./CUCjtGpu.js";import"./Dhs1Or-2.js";import"./CUvT7aun.js";import"./TLA9Fm80.js";import"./Dm_OpIlv.js";import"./CU-snwr6.js";import"./DNI0JtzU.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="03fc55bd-87e9-45de-91c6-65720b2909c5",e._sentryDebugIdIdentifier="sentry-dbid-03fc55bd-87e9-45de-91c6-65720b2909c5")}catch{}})();const a=u({originalTitle:"Test Audio",sensitivity:[],isSensitive:!1}),b={render:e=>({template:`
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
