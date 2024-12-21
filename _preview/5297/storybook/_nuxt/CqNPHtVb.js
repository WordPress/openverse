import{S as n}from"./BxCgZ025.js";import{_ as a}from"./CBXeRDLZ.js";import"./D6xGyQxu.js";import{h as l,d}from"./Bf-AzR54.js";import"./BnJZTjE_.js";import"./CkK3diBk.js";import"./CUyQTIYr.js";import"./BsG3jt0b.js";import"./CRElLIkf.js";import"./B06Wl6je.js";import"./C7lp-ITr.js";import"./BZTl3SGY.js";import"./SxvBqf-I.js";import"./BvQxCwAx.js";import"./Tu1w6jvB.js";import"./DBWmBUzF.js";import"./eAGCzEdq.js";import"./G0IPDLoE.js";import"./DzAq6MI-.js";import"./D3fY7LA9.js";import"./EvZx83Uz.js";import"./p8nc5Li4.js";import"./DmNhhvCU.js";import"./CO4aZKIX.js";import"./DhTbjJlp.js";import"./6ItBZc85.js";import"./v8hTCxed.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="8d1e416c-d272-46a9-86ea-a9a9427055b1",e._sentryDebugIdIdentifier="sentry-dbid-8d1e416c-d272-46a9-86ea-a9a9427055b1")}catch{}})();const i=d({name:"VSafetyWallWrapper",components:{VSafetyWall:a},props:{id:{type:String,required:!0},sensitivities:{type:Array,default:()=>[]}},emits:["reveal"],setup(e,{emit:t}){const o=()=>t("reveal");return()=>l(a,{id:e.id,sensitivity:e.sensitivities,onReveal:o})}}),F={title:"Components/VSafetyWall",component:i,argTypes:{sensitivities:{control:{type:"check"},options:n},onReveal:{action:"reveal"}},args:{sensitivities:[...n],id:"f9384235-b72e-4f1e-9b05-e1b116262a29"}},r={render:e=>({components:{VSafetyWallWrapper:i},setup(){const t=()=>{console.log("Revealed")};return()=>l(i,{id:e.id,sensitivity:e.sensitivities,onReveal:t})}}),name:"default"};var s,p,m;r.parameters={...r.parameters,docs:{...(s=r.parameters)==null?void 0:s.docs,source:{originalSource:`{
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
