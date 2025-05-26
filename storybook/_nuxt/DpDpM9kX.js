import{h as l,d}from"./53SD24Bo.js";import{S as n}from"./MJVc8exl.js";import{_ as s}from"./yE_o5zxM.js";import"./ey6Ec0eW.js";import"./B_xeuOb0.js";import"./CD1OwZH3.js";import"./BPAP40Rv.js";import"./BhptSssS.js";import"./D6STwiFZ.js";import"./7RO02bE1.js";import"./uTbLe7kf.js";import"./C0_S5Dz7.js";import"./D8YLUWro.js";import"./ETC5RdxK.js";import"./Bcilh3GR.js";import"./C81jPTEF.js";import"./QQWdHC9P.js";import"./DhVXE6x0.js";import"./okj3qyDJ.js";import"./Cw5DoNPI.js";import"./Bdn_xeD6.js";import"./B7QaUHa9.js";import"./CCSsdpEp.js";import"./BxMTa-Rq.js";import"./DhTbjJlp.js";import"./DtcCBiui.js";import"./DzXFAWuk.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="09d0864e-57e2-4a4f-a34e-1794775a7d00",e._sentryDebugIdIdentifier="sentry-dbid-09d0864e-57e2-4a4f-a34e-1794775a7d00")}catch{}})();const i=d({name:"VSafetyWallWrapper",components:{VSafetyWall:s},props:{id:{type:String,required:!0},sensitivities:{type:Array,default:()=>[]}},emits:["reveal"],setup(e,{emit:t}){const o=()=>t("reveal");return()=>l(s,{id:e.id,sensitivity:e.sensitivities,onReveal:o})}}),F={title:"Components/VSafetyWall",component:i,argTypes:{sensitivities:{control:{type:"check"},options:n},onReveal:{action:"reveal"}},args:{sensitivities:[...n],id:"f9384235-b72e-4f1e-9b05-e1b116262a29"}},r={render:e=>({components:{VSafetyWallWrapper:i},setup(){const t=()=>{console.log("Revealed")};return()=>l(i,{id:e.id,sensitivity:e.sensitivities,onReveal:t})}}),name:"default"};var a,p,m;r.parameters={...r.parameters,docs:{...(a=r.parameters)==null?void 0:a.docs,source:{originalSource:`{
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
