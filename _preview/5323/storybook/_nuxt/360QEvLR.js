import{h as l,d}from"./DwwldUEF.js";import{S as n}from"./BNZBDzqs.js";import{_ as s}from"./CAhgDxSj.js";import"./_APRZIM1.js";import"./CVIvqSzo.js";import"./B6xXmqkp.js";import"./hEU2uDsT.js";import"./DbbxtPJM.js";import"./BAbDw2j1.js";import"./Ck0CgHQL.js";import"./Chgn5vcY.js";import"./DfKQSGJ_.js";import"./HE8VvABB.js";import"./BZyg411k.js";import"./--8yokH5.js";import"./D2_E7_fN.js";import"./BcTEa7d-.js";import"./zgpsPOGm.js";import"./DzAq6MI-.js";import"./5Ry8iPjm.js";import"./Dy2lpsBJ.js";import"./Dv6gP7wZ.js";import"./erT4Ktbo.js";import"./zDkj65pD.js";import"./DhTbjJlp.js";import"./D197vL4o.js";import"./DS5pDSwp.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="09d0864e-57e2-4a4f-a34e-1794775a7d00",e._sentryDebugIdIdentifier="sentry-dbid-09d0864e-57e2-4a4f-a34e-1794775a7d00")}catch{}})();const i=d({name:"VSafetyWallWrapper",components:{VSafetyWall:s},props:{id:{type:String,required:!0},sensitivities:{type:Array,default:()=>[]}},emits:["reveal"],setup(e,{emit:t}){const o=()=>t("reveal");return()=>l(s,{id:e.id,sensitivity:e.sensitivities,onReveal:o})}}),F={title:"Components/VSafetyWall",component:i,argTypes:{sensitivities:{control:{type:"check"},options:n},onReveal:{action:"reveal"}},args:{sensitivities:[...n],id:"f9384235-b72e-4f1e-9b05-e1b116262a29"}},r={render:e=>({components:{VSafetyWallWrapper:i},setup(){const t=()=>{console.log("Revealed")};return()=>l(i,{id:e.id,sensitivity:e.sensitivities,onReveal:t})}}),name:"default"};var a,p,m;r.parameters={...r.parameters,docs:{...(a=r.parameters)==null?void 0:a.docs,source:{originalSource:`{
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
