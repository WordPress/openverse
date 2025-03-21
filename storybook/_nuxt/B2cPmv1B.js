import{i as t}from"./DNsxMNRe.js";import{g as u}from"./BZltekj6.js";import{V as n,g as m}from"./DQEbo7Wm.js";import{u as f}from"./B5GQZ6KW.js";import{_ as l}from"./CV3lOE8b.js";import{u as g}from"./B9Cuo1Ro.js";import"./DBIAFgjH.js";import"./BMTpeGZl.js";import"./DQdiNp-F.js";import"./53SD24Bo.js";import"./DJCDDsZ8.js";import"./BkiQmg8E.js";import"./Bji7sDXf.js";import"./CLb7Coka.js";import"./okj3qyDJ.js";import"./Bb2yh_vr.js";import"./BYpqqPRZ.js";import"./BRl0LMB0.js";import"./DiSpNEja.js";import"./BNCCbueK.js";import"./DuKV0Hy2.js";import"./DhTbjJlp.js";import"./CEoqXQdM.js";import"./Z6giSmwE.js";import"./6gBMcAY7.js";import"./BwPl7lue.js";import"./CBc_U4V9.js";import"./qH-7fQ0Y.js";import"./5qOHoM0Q.js";import"./BQrorSEU.js";import"./B06vE1PI.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="03fc55bd-87e9-45de-91c6-65720b2909c5",e._sentryDebugIdIdentifier="sentry-dbid-03fc55bd-87e9-45de-91c6-65720b2909c5")}catch{}})();const a=u({originalTitle:"Test Audio",sensitivity:[],isSensitive:!1}),b={render:e=>({template:`
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
