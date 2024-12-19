import{i as t}from"./CnjFSr40.js";import{g as u}from"./DwJsYYLD.js";import{V as n,g as m}from"./n8FfjIbw.js";import{u as l}from"./C1-0vP3w.js";import{_ as f}from"./yTaY3Upu.js";import{u as g}from"./FADBYOvo.js";import"./CDFarRZf.js";import"./UQnQ_SvL.js";import"./olEHfY3b.js";import"./B78A4_tv.js";import"./DapBWOOs.js";import"./shqyu_m_.js";import"./Bf-AzR54.js";import"./BF6vVg7M.js";import"./DzAq6MI-.js";import"./CADoQZ_l.js";import"./nHVt-A68.js";import"./Big7CaLo.js";import"./bYPJlIeP.js";import"./HitohTq8.js";import"./8vSlX9Dy.js";import"./DhTbjJlp.js";import"./D9JVarWf.js";import"./_8muH8lI.js";import"./Z4GvL5Sf.js";import"./DTP0RB-8.js";import"./G-2gs7Wx.js";import"./Xl6n5ahl.js";import"./DP0Qqza0.js";import"./DdzDG7_q.js";import"./BkbAmEqc.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="6d45c3e1-8bd0-49c0-945e-5d2845d05d15",e._sentryDebugIdIdentifier="sentry-dbid-6d45c3e1-8bd0-49c0-945e-5d2845d05d15")}catch{}})();const a=u({originalTitle:"Test Audio",sensitivity:[],isSensitive:!1}),y={render:e=>({template:`
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
