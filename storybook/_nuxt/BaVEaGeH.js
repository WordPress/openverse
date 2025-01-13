import{h as l,d}from"./DwwldUEF.js";import{S as n}from"./DyntKXIc.js";import{_ as s}from"./CFmpschG.js";import"./BKd6qjwJ.js";import"./B_JavP0r.js";import"./DyjmqLvs.js";import"./TJSYFxys.js";import"./DXt3Hw-9.js";import"./DrQM85Nc.js";import"./Ck0CgHQL.js";import"./DeIUwsAH.js";import"./Bc_6hboB.js";import"./BJKkpTjt.js";import"./DIa_evZO.js";import"./D5nIdk7e.js";import"./DEzOOYTC.js";import"./BA2RD0IG.js";import"./BwtrEtqR.js";import"./DzAq6MI-.js";import"./B7G-YaxP.js";import"./Efi66Qad.js";import"./DjJGxhuO.js";import"./D318SDY2.js";import"./BMyQprRt.js";import"./DhTbjJlp.js";import"./R_--_Flr.js";import"./Duzn9Bak.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="09d0864e-57e2-4a4f-a34e-1794775a7d00",e._sentryDebugIdIdentifier="sentry-dbid-09d0864e-57e2-4a4f-a34e-1794775a7d00")}catch{}})();const i=d({name:"VSafetyWallWrapper",components:{VSafetyWall:s},props:{id:{type:String,required:!0},sensitivities:{type:Array,default:()=>[]}},emits:["reveal"],setup(e,{emit:t}){const o=()=>t("reveal");return()=>l(s,{id:e.id,sensitivity:e.sensitivities,onReveal:o})}}),F={title:"Components/VSafetyWall",component:i,argTypes:{sensitivities:{control:{type:"check"},options:n},onReveal:{action:"reveal"}},args:{sensitivities:[...n],id:"f9384235-b72e-4f1e-9b05-e1b116262a29"}},r={render:e=>({components:{VSafetyWallWrapper:i},setup(){const t=()=>{console.log("Revealed")};return()=>l(i,{id:e.id,sensitivity:e.sensitivities,onReveal:t})}}),name:"default"};var a,p,m;r.parameters={...r.parameters,docs:{...(a=r.parameters)==null?void 0:a.docs,source:{originalSource:`{
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
