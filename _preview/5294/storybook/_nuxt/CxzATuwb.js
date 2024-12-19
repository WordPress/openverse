import{i as t}from"./kxlZ8p9x.js";import{g as u}from"./DoPpxw1p.js";import{V as n,g as m}from"./Cqo_9mNF.js";import{u as l}from"./DUj0lNLx.js";import{_ as f}from"./82JfriN_.js";import{u as g}from"./FADBYOvo.js";import"./DzKe1FZy.js";import"./BKlnuUDG.js";import"./uHJqFrjm.js";import"./C1x2Pz8-.js";import"./yiMr7TA-.js";import"./DypQgoql.js";import"./Bf-AzR54.js";import"./DEFsxmui.js";import"./DzAq6MI-.js";import"./Mi53UD0-.js";import"./BdGbGJtZ.js";import"./KaIp0RKv.js";import"./Imyqroa4.js";import"./sL22Kbl4.js";import"./CYExI-7Z.js";import"./DhTbjJlp.js";import"./D9JVarWf.js";import"./BmQ_sOpV.js";import"./D6X2gOn4.js";import"./CAl9Yp-W.js";import"./2X7CKgv5.js";import"./DJpKulq8.js";import"./RE842jSx.js";import"./WNyId_Bm.js";import"./BkbAmEqc.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="6d45c3e1-8bd0-49c0-945e-5d2845d05d15",e._sentryDebugIdIdentifier="sentry-dbid-6d45c3e1-8bd0-49c0-945e-5d2845d05d15")}catch{}})();const a=u({originalTitle:"Test Audio",sensitivity:[],isSensitive:!1}),y={render:e=>({template:`
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
