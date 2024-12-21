import{i as t}from"./RD7-kRRR.js";import{g as u}from"./CZ1Tuwkw.js";import{V as n,g as m}from"./5cgvE6HC.js";import{u as l}from"./MEtS268D.js";import{_ as f}from"./ChB37Lba.js";import{u as g}from"./FADBYOvo.js";import"./Cb7Zuqx8.js";import"./CMfearWB.js";import"./Bqz7oJe_.js";import"./Dy3_0OnD.js";import"./CkisY6KX.js";import"./BiC8Cn9J.js";import"./Bf-AzR54.js";import"./CaHoH0jp.js";import"./DzAq6MI-.js";import"./D0sNZIq0.js";import"./LrXbMvc1.js";import"./53t0DvQJ.js";import"./CXyLtIA_.js";import"./4JVUVGS7.js";import"./BtGjuzI1.js";import"./DhTbjJlp.js";import"./D9JVarWf.js";import"./QA3pXhHS.js";import"./B_InzCW8.js";import"./BTMV7jrV.js";import"./Dbp9NDS0.js";import"./CaLJbFDg.js";import"./OXefpJAj.js";import"./BfGnB64-.js";import"./BkbAmEqc.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="6d45c3e1-8bd0-49c0-945e-5d2845d05d15",e._sentryDebugIdIdentifier="sentry-dbid-6d45c3e1-8bd0-49c0-945e-5d2845d05d15")}catch{}})();const a=u({originalTitle:"Test Audio",sensitivity:[],isSensitive:!1}),y={render:e=>({template:`
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
  `,components:{VMetadata:n,VLanguageSelect:f},setup(){l().$patch({providers:{audio:[{source_name:a.source}],image:[{source_name:t.source}]},sourceNames:{audio:[a.source],image:[t.source]}});const{t:i}=g({useScope:"global"}),c=[{metadata:m(t,i,{width:t.width,height:t.height,type:t.filetype}),media:t},{metadata:m(a,i),media:a}];return{args:e,data:c}}})},U={title:"Components/VMediaInfo/VMetadata",component:n},o={...y,name:"VMetadata"};var d,s,p;o.parameters={...o.parameters,docs:{...(d=o.parameters)==null?void 0:d.docs,source:{originalSource:`{
  ...Template,
  name: "VMetadata"
}`,...(p=(s=o.parameters)==null?void 0:s.docs)==null?void 0:p.source}}};const W=["Default"];export{o as Default,W as __namedExportsOrder,U as default};
