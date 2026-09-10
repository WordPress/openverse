import{i as t}from"./Bi73_qhu.js";import{g as u}from"./D8ZmAXon.js";import{V as n,g as d}from"./K0F_r4l-.js";import{u as f}from"./CdxtYFZI.js";import{_ as l}from"./BopUQEOl.js";import{u as g}from"./B9Cuo1Ro.js";import"./_bbq3c9C.js";import"./DDS--uLL.js";import"./Cy_NKsXi.js";import"./53SD24Bo.js";import"./iProge2w.js";import"./DONNfqqY.js";import"./DZOi7sP9.js";import"./CUnsfT8r.js";import"./okj3qyDJ.js";import"./BOewZ2sR.js";import"./D2GrBf-6.js";import"./DjsporFN.js";import"./B_-6Taiq.js";import"./CH5-dTGy.js";import"./dvXbmdTd.js";import"./ivjvpZKc.js";import"./DhTbjJlp.js";import"./fNRj2RrI.js";import"./BlDvZdzq.js";import"./xQ8_qGND.js";import"./DlboKt2a.js";import"./Di7dAt70.js";import"./B9k6C3Hw.js";import"./qbya_cPS.js";import"./BQrorSEU.js";import"./B06vE1PI.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="da396fd4-0b19-4c5e-8d81-d56ddd4fc742",e._sentryDebugIdIdentifier="sentry-dbid-da396fd4-0b19-4c5e-8d81-d56ddd4fc742")}catch{}})();const a=u({originalTitle:"Test Audio",sensitivity:[],isSensitive:!1}),y={render:e=>({template:`
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
  `,components:{VMetadata:n,VLanguageSelect:l},setup(){f().$patch({providers:{audio:[{source_name:a.source}],image:[{source_name:t.source}]},sourceNames:{audio:[a.source],image:[t.source]}});const{t:i}=g({useScope:"global"}),c=[{metadata:d(t,i,{width:t.width,height:t.height,type:t.filetype}),media:t},{metadata:d(a,i),media:a}];return{args:e,data:c}}})},W={title:"Components/VMediaInfo/VMetadata",component:n},o={...y,name:"VMetadata"};var m,s,p;o.parameters={...o.parameters,docs:{...(m=o.parameters)==null?void 0:m.docs,source:{originalSource:`{
  ...Template,
  name: "VMetadata"
}`,...(p=(s=o.parameters)==null?void 0:s.docs)==null?void 0:p.source}}};const X=["Default"];export{o as Default,X as __namedExportsOrder,W as default};
