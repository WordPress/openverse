import{S as n}from"./DmC3CRu-.js";import{_ as a}from"./BV7U1f4Z.js";import"./DzKe1FZy.js";import{h as l,d}from"./Bf-AzR54.js";import"./DypQgoql.js";import"./BKlnuUDG.js";import"./B5T0JkOB.js";import"./meB9zTZj.js";import"./RE842jSx.js";import"./B06Wl6je.js";import"./BqixEy0E.js";import"./CbeNxiKf.js";import"./C1x2Pz8-.js";import"./DUj0lNLx.js";import"./uHJqFrjm.js";import"./Imyqroa4.js";import"./P6N_4fLa.js";import"./DEFsxmui.js";import"./DzAq6MI-.js";import"./Mi53UD0-.js";import"./BdGbGJtZ.js";import"./KaIp0RKv.js";import"./sL22Kbl4.js";import"./CYExI-7Z.js";import"./DhTbjJlp.js";import"./2X7CKgv5.js";import"./DJpKulq8.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="8d1e416c-d272-46a9-86ea-a9a9427055b1",e._sentryDebugIdIdentifier="sentry-dbid-8d1e416c-d272-46a9-86ea-a9a9427055b1")}catch{}})();const i=d({name:"VSafetyWallWrapper",components:{VSafetyWall:a},props:{id:{type:String,required:!0},sensitivities:{type:Array,default:()=>[]}},emits:["reveal"],setup(e,{emit:t}){const o=()=>t("reveal");return()=>l(a,{id:e.id,sensitivity:e.sensitivities,onReveal:o})}}),F={title:"Components/VSafetyWall",component:i,argTypes:{sensitivities:{control:{type:"check"},options:n},onReveal:{action:"reveal"}},args:{sensitivities:[...n],id:"f9384235-b72e-4f1e-9b05-e1b116262a29"}},r={render:e=>({components:{VSafetyWallWrapper:i},setup(){const t=()=>{console.log("Revealed")};return()=>l(i,{id:e.id,sensitivity:e.sensitivities,onReveal:t})}}),name:"default"};var s,p,m;r.parameters={...r.parameters,docs:{...(s=r.parameters)==null?void 0:s.docs,source:{originalSource:`{
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
