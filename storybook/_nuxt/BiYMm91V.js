import{h as l,d}from"./53SD24Bo.js";import{S as n}from"./Cu8oCyfM.js";import{_ as s}from"./C-g9qDkO.js";import"./DxXQfK2h.js";import"./DEUQKZ_9.js";import"./CGl8BGyI.js";import"./Bl44UfZi.js";import"./CrtbdNAL.js";import"./BfmvDfJj.js";import"./7RO02bE1.js";import"./7T7Oyunt.js";import"./aM5GB1sa.js";import"./JKyArXdZ.js";import"./CnJShkNX.js";import"./Ca-grqql.js";import"./GK6z1vC-.js";import"./CJn6N6md.js";import"./DCBI9Hp4.js";import"./okj3qyDJ.js";import"./COHSvtot.js";import"./CbQ_U0bA.js";import"./1q_AdtTO.js";import"./CO_nLv6a.js";import"./DY7Jae7t.js";import"./DhTbjJlp.js";import"./Do357AjE.js";import"./Ab-gfhxw.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="09d0864e-57e2-4a4f-a34e-1794775a7d00",e._sentryDebugIdIdentifier="sentry-dbid-09d0864e-57e2-4a4f-a34e-1794775a7d00")}catch{}})();const i=d({name:"VSafetyWallWrapper",components:{VSafetyWall:s},props:{id:{type:String,required:!0},sensitivities:{type:Array,default:()=>[]}},emits:["reveal"],setup(e,{emit:t}){const o=()=>t("reveal");return()=>l(s,{id:e.id,sensitivity:e.sensitivities,onReveal:o})}}),F={title:"Components/VSafetyWall",component:i,argTypes:{sensitivities:{control:{type:"check"},options:n},onReveal:{action:"reveal"}},args:{sensitivities:[...n],id:"f9384235-b72e-4f1e-9b05-e1b116262a29"}},r={render:e=>({components:{VSafetyWallWrapper:i},setup(){const t=()=>{console.log("Revealed")};return()=>l(i,{id:e.id,sensitivity:e.sensitivities,onReveal:t})}}),name:"default"};var a,p,m;r.parameters={...r.parameters,docs:{...(a=r.parameters)==null?void 0:a.docs,source:{originalSource:`{
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
