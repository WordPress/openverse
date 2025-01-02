import{i as t}from"./TZuTWBIL.js";import{g as u}from"./BaNM9SCq.js";import{V as n,g as m}from"./BlnhJJiG.js";import{u as l}from"./DtxX-pIl.js";import{_ as f}from"./BqKDY6C-.js";import{u as g}from"./FADBYOvo.js";import"./DHOw7aFH.js";import"./CyBFP4Sd.js";import"./CS7XnKLR.js";import"./BYhZ12lc.js";import"./QuKN6SOG.js";import"./DZFv-zsC.js";import"./Bf-AzR54.js";import"./7n6WcIxw.js";import"./DzAq6MI-.js";import"./Btjq2moo.js";import"./rdZXP2j6.js";import"./DMScrd9r.js";import"./BUZMDrXj.js";import"./lASKgZAk.js";import"./DnikNTKn.js";import"./DhTbjJlp.js";import"./D9JVarWf.js";import"./BFr0hRu6.js";import"./UOk5Tr0e.js";import"./BitPUtzJ.js";import"./DG5kPZbt.js";import"./CTiRmcG7.js";import"./Btoo3kXe.js";import"./D1XzvLFr.js";import"./BkbAmEqc.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="6d45c3e1-8bd0-49c0-945e-5d2845d05d15",e._sentryDebugIdIdentifier="sentry-dbid-6d45c3e1-8bd0-49c0-945e-5d2845d05d15")}catch{}})();const a=u({originalTitle:"Test Audio",sensitivity:[],isSensitive:!1}),y={render:e=>({template:`
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
