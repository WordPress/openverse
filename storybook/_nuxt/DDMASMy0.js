import{S as n}from"./Nz2p3Woh.js";import{_ as a}from"./BPZfUWyA.js";import"./CDFarRZf.js";import{h as l,d}from"./Bf-AzR54.js";import"./shqyu_m_.js";import"./UQnQ_SvL.js";import"./BOvEjOPJ.js";import"./DHILWyHo.js";import"./DP0Qqza0.js";import"./B06Wl6je.js";import"./6POF_SQB.js";import"./nResBSny.js";import"./B78A4_tv.js";import"./C1-0vP3w.js";import"./olEHfY3b.js";import"./bYPJlIeP.js";import"./rZ73O98I.js";import"./BF6vVg7M.js";import"./DzAq6MI-.js";import"./CADoQZ_l.js";import"./nHVt-A68.js";import"./Big7CaLo.js";import"./HitohTq8.js";import"./8vSlX9Dy.js";import"./DhTbjJlp.js";import"./G-2gs7Wx.js";import"./Xl6n5ahl.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="8d1e416c-d272-46a9-86ea-a9a9427055b1",e._sentryDebugIdIdentifier="sentry-dbid-8d1e416c-d272-46a9-86ea-a9a9427055b1")}catch{}})();const i=d({name:"VSafetyWallWrapper",components:{VSafetyWall:a},props:{id:{type:String,required:!0},sensitivities:{type:Array,default:()=>[]}},emits:["reveal"],setup(e,{emit:t}){const o=()=>t("reveal");return()=>l(a,{id:e.id,sensitivity:e.sensitivities,onReveal:o})}}),F={title:"Components/VSafetyWall",component:i,argTypes:{sensitivities:{control:{type:"check"},options:n},onReveal:{action:"reveal"}},args:{sensitivities:[...n],id:"f9384235-b72e-4f1e-9b05-e1b116262a29"}},r={render:e=>({components:{VSafetyWallWrapper:i},setup(){const t=()=>{console.log("Revealed")};return()=>l(i,{id:e.id,sensitivity:e.sensitivities,onReveal:t})}}),name:"default"};var s,p,m;r.parameters={...r.parameters,docs:{...(s=r.parameters)==null?void 0:s.docs,source:{originalSource:`{
  render: args => ({
    components: {
      VSafetyWallWrapper
    },
    setup() {
      const logReveal = () => {
        console.log("Revealed");
      };
      return () => h(VSafetyWallWrapper, {
        id: args.id,
        sensitivity: args.sensitivities,
        onReveal: logReveal
      });
    }
  }),
  name: "default"
}`,...(m=(p=r.parameters)==null?void 0:p.docs)==null?void 0:m.source}}};const G=["Default"];export{r as Default,G as __namedExportsOrder,F as default};
