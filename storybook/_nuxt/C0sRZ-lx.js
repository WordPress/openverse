import{h as l,d}from"./53SD24Bo.js";import{S as n}from"./DD0JbomO.js";import{_ as a}from"./d1UcdOBH.js";import"./_bbq3c9C.js";import"./DZOi7sP9.js";import"./DDS--uLL.js";import"./DGyM8Eie.js";import"./DVthAQU8.js";import"./B9k6C3Hw.js";import"./7RO02bE1.js";import"./8DNOLO2n.js";import"./C1DVfU3S.js";import"./iProge2w.js";import"./CdxtYFZI.js";import"./Cy_NKsXi.js";import"./B_-6Taiq.js";import"./Dm0sd39P.js";import"./CUnsfT8r.js";import"./okj3qyDJ.js";import"./BOewZ2sR.js";import"./D2GrBf-6.js";import"./DjsporFN.js";import"./CH5-dTGy.js";import"./dvXbmdTd.js";import"./ivjvpZKc.js";import"./DhTbjJlp.js";import"./DlboKt2a.js";import"./Di7dAt70.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="4ffab61e-292a-4ca5-8ee8-9a1cdf755cc9",e._sentryDebugIdIdentifier="sentry-dbid-4ffab61e-292a-4ca5-8ee8-9a1cdf755cc9")}catch{}})();const i=d({name:"VSafetyWallWrapper",components:{VSafetyWall:a},props:{id:{type:String,required:!0},sensitivities:{type:Array,default:()=>[]}},emits:["reveal"],setup(e,{emit:t}){const o=()=>t("reveal");return()=>l(a,{id:e.id,sensitivity:e.sensitivities,onReveal:o})}}),G={title:"Components/VSafetyWall",component:i,argTypes:{sensitivities:{control:{type:"check"},options:n},onReveal:{action:"reveal"}},args:{sensitivities:[...n],id:"f9384235-b72e-4f1e-9b05-e1b116262a29"}},r={render:e=>({components:{VSafetyWallWrapper:i},setup(){const t=()=>{console.log("Revealed")};return()=>l(i,{id:e.id,sensitivity:e.sensitivities,onReveal:t})}}),name:"default"};var s,p,m;r.parameters={...r.parameters,docs:{...(s=r.parameters)==null?void 0:s.docs,source:{originalSource:`{
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
}`,...(m=(p=r.parameters)==null?void 0:p.docs)==null?void 0:m.source}}};const H=["Default"];export{r as Default,H as __namedExportsOrder,G as default};
