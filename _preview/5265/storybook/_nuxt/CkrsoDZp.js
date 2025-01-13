import{h as l,d}from"./DwwldUEF.js";import{S as n}from"./Gc5ScyLZ.js";import{_ as s}from"./Ckry8uTP.js";import"./CjQ0HQF0.js";import"./C6VqcP4x.js";import"./CFZbsX2Q.js";import"./Ley1esUq.js";import"./C0pA7UPR.js";import"./rq0rg1X-.js";import"./Ck0CgHQL.js";import"./CUsfujdM.js";import"./DmsD6orq.js";import"./BIohVJVH.js";import"./KlWK2kB1.js";import"./CD6Nr1ia.js";import"./BufT_yKp.js";import"./BuC5_mLh.js";import"./DcMSHMAp.js";import"./DzAq6MI-.js";import"./B67cIdux.js";import"./Cqs9wCPQ.js";import"./D9b6d0V7.js";import"./Bu-vEs7l.js";import"./Dwl_h6Xz.js";import"./DhTbjJlp.js";import"./Bl4H7SX1.js";import"./DZZ1Fr_1.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="09d0864e-57e2-4a4f-a34e-1794775a7d00",e._sentryDebugIdIdentifier="sentry-dbid-09d0864e-57e2-4a4f-a34e-1794775a7d00")}catch{}})();const i=d({name:"VSafetyWallWrapper",components:{VSafetyWall:s},props:{id:{type:String,required:!0},sensitivities:{type:Array,default:()=>[]}},emits:["reveal"],setup(e,{emit:t}){const o=()=>t("reveal");return()=>l(s,{id:e.id,sensitivity:e.sensitivities,onReveal:o})}}),F={title:"Components/VSafetyWall",component:i,argTypes:{sensitivities:{control:{type:"check"},options:n},onReveal:{action:"reveal"}},args:{sensitivities:[...n],id:"f9384235-b72e-4f1e-9b05-e1b116262a29"}},r={render:e=>({components:{VSafetyWallWrapper:i},setup(){const t=()=>{console.log("Revealed")};return()=>l(i,{id:e.id,sensitivity:e.sensitivities,onReveal:t})}}),name:"default"};var a,p,m;r.parameters={...r.parameters,docs:{...(a=r.parameters)==null?void 0:a.docs,source:{originalSource:`{
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
