import{S as n}from"./DRZycMl_.js";import{_ as a}from"./DuDnsK1n.js";import"./Cvwh1eWU.js";import{h as l,d}from"./Bf-AzR54.js";import"./DrjqGyIn.js";import"./Dhd2LSaJ.js";import"./t9mHqYU6.js";import"./CB4cLo_T.js";import"./DyOcfQEa.js";import"./B06Wl6je.js";import"./BBH6I9DT.js";import"./D925bKRv.js";import"./Ky12kILv.js";import"./ZDkF8ik7.js";import"./C1bAmx5w.js";import"./B7SSP_u7.js";import"./DU1fxRpF.js";import"./DeByBTAG.js";import"./DzAq6MI-.js";import"./C6fyqnb4.js";import"./B8OOORiY.js";import"./D4xJYYnt.js";import"./C6PVQces.js";import"./H3MvUUlX.js";import"./DhTbjJlp.js";import"./DfdPflxj.js";import"./CYAItMv8.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="8d1e416c-d272-46a9-86ea-a9a9427055b1",e._sentryDebugIdIdentifier="sentry-dbid-8d1e416c-d272-46a9-86ea-a9a9427055b1")}catch{}})();const i=d({name:"VSafetyWallWrapper",components:{VSafetyWall:a},props:{id:{type:String,required:!0},sensitivities:{type:Array,default:()=>[]}},emits:["reveal"],setup(e,{emit:t}){const o=()=>t("reveal");return()=>l(a,{id:e.id,sensitivity:e.sensitivities,onReveal:o})}}),F={title:"Components/VSafetyWall",component:i,argTypes:{sensitivities:{control:{type:"check"},options:n},onReveal:{action:"reveal"}},args:{sensitivities:[...n],id:"f9384235-b72e-4f1e-9b05-e1b116262a29"}},r={render:e=>({components:{VSafetyWallWrapper:i},setup(){const t=()=>{console.log("Revealed")};return()=>l(i,{id:e.id,sensitivity:e.sensitivities,onReveal:t})}}),name:"default"};var s,p,m;r.parameters={...r.parameters,docs:{...(s=r.parameters)==null?void 0:s.docs,source:{originalSource:`{
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
