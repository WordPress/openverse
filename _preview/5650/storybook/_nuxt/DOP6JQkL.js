import{i as t}from"./BgU5ZoOE.js";import{g as u}from"./B8yjhL4L.js";import{V as n,g as m}from"./BW7rcHQ9.js";import{u as f}from"./CdQaOBNt.js";import{_ as l}from"./B_lp3KKM.js";import{u as g}from"./D5Za6x0E.js";import"./Cre_5D1H.js";import"./BWJ9rAf_.js";import"./C7sHCGoX.js";import"./DmrXErv4.js";import"./wMBvb-CP.js";import"./BAdK41rD.js";import"./P7ZX4TMp.js";import"./CT8Zrxvs.js";import"./DzAq6MI-.js";import"./DWRfakdt.js";import"./CCN4kZnP.js";import"./Bn7RUpRV.js";import"./B_dsH32H.js";import"./OMXwMIS8.js";import"./rMKLwKwR.js";import"./Dv0Nl23j.js";import"./DhTbjJlp.js";import"./DG4S0cIi.js";import"./C7pLFojh.js";import"./zcyFsLMi.js";import"./BRHrr7ck.js";import"./Bpr67t9y.js";import"./B3KNKrKa.js";import"./B2mcawKa.js";import"./Dx-3nI8A.js";import"./CJ7FTku9.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="518c23a7-6712-40e6-bf1d-4475ef041dfd",e._sentryDebugIdIdentifier="sentry-dbid-518c23a7-6712-40e6-bf1d-4475ef041dfd")}catch{}})();const a=u({originalTitle:"Test Audio",sensitivity:[],isSensitive:!1}),y={render:e=>({template:`
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
  `,components:{VMetadata:n,VLanguageSelect:l},setup(){f().$patch({providers:{audio:[{source_name:a.source}],image:[{source_name:t.source}]},sourceNames:{audio:[a.source],image:[t.source]}});const{t:i}=g({useScope:"global"}),c=[{metadata:m(t,i,{width:t.width,height:t.height,type:t.filetype}),media:t},{metadata:m(a,i),media:a}];return{args:e,data:c}}})},W={title:"Components/VMediaInfo/VMetadata",component:n},o={...y,name:"VMetadata"};var s,d,p;o.parameters={...o.parameters,docs:{...(s=o.parameters)==null?void 0:s.docs,source:{originalSource:`{
  ...Template,
  name: "VMetadata"
}`,...(p=(d=o.parameters)==null?void 0:d.docs)==null?void 0:p.source}}};const X=["Default"];export{o as Default,X as __namedExportsOrder,W as default};
