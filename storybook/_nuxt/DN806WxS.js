import{h as l,d}from"./53SD24Bo.js";import{S as n}from"./CI6-PtcM.js";import{_ as s}from"./d1_U3llv.js";import"./Bk8VSEei.js";import"./D4B1y8Wp.js";import"./BSHtV9yS.js";import"./DBpyOWk7.js";import"./Cx3b_-up.js";import"./DLXib-Qm.js";import"./7RO02bE1.js";import"./7RAMVlBS.js";import"./CA_M5S-4.js";import"./whaKyvbR.js";import"./DZSCtjcm.js";import"./DUD5NJ41.js";import"./D1l3oJXo.js";import"./B8akBo1x.js";import"./S07_m3Bd.js";import"./okj3qyDJ.js";import"./Cbq1TCLb.js";import"./fL1fV1YB.js";import"./C7m8LBdt.js";import"./CQ3yco75.js";import"./b8e1KD_n.js";import"./DhTbjJlp.js";import"./Cpzk_0_B.js";import"./Bl5m8s2n.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="09d0864e-57e2-4a4f-a34e-1794775a7d00",e._sentryDebugIdIdentifier="sentry-dbid-09d0864e-57e2-4a4f-a34e-1794775a7d00")}catch{}})();const i=d({name:"VSafetyWallWrapper",components:{VSafetyWall:s},props:{id:{type:String,required:!0},sensitivities:{type:Array,default:()=>[]}},emits:["reveal"],setup(e,{emit:t}){const o=()=>t("reveal");return()=>l(s,{id:e.id,sensitivity:e.sensitivities,onReveal:o})}}),F={title:"Components/VSafetyWall",component:i,argTypes:{sensitivities:{control:{type:"check"},options:n},onReveal:{action:"reveal"}},args:{sensitivities:[...n],id:"f9384235-b72e-4f1e-9b05-e1b116262a29"}},r={render:e=>({components:{VSafetyWallWrapper:i},setup(){const t=()=>{console.log("Revealed")};return()=>l(i,{id:e.id,sensitivity:e.sensitivities,onReveal:t})}}),name:"default"};var a,p,m;r.parameters={...r.parameters,docs:{...(a=r.parameters)==null?void 0:a.docs,source:{originalSource:`{
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
