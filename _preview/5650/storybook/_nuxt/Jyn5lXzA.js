import{h as l,d}from"./DmrXErv4.js";import{S as n}from"./Boj1x2qa.js";import{_ as s}from"./D2AHTsCE.js";import"./Cre_5D1H.js";import"./P7ZX4TMp.js";import"./BWJ9rAf_.js";import"./D8RLh9Dr.js";import"./DFZUF_34.js";import"./B3KNKrKa.js";import"./BxtqxG2r.js";import"./D7WD_DXd.js";import"./D_KYnWat.js";import"./wMBvb-CP.js";import"./CdQaOBNt.js";import"./C7sHCGoX.js";import"./B_dsH32H.js";import"./CEG4L8Wc.js";import"./CT8Zrxvs.js";import"./DzAq6MI-.js";import"./DWRfakdt.js";import"./CCN4kZnP.js";import"./Bn7RUpRV.js";import"./OMXwMIS8.js";import"./rMKLwKwR.js";import"./Dv0Nl23j.js";import"./DhTbjJlp.js";import"./BRHrr7ck.js";import"./Bpr67t9y.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="9e5fcd08-1a90-44d9-83f6-972a51105ac9",e._sentryDebugIdIdentifier="sentry-dbid-9e5fcd08-1a90-44d9-83f6-972a51105ac9")}catch{}})();const i=d({name:"VSafetyWallWrapper",components:{VSafetyWall:s},props:{id:{type:String,required:!0},sensitivities:{type:Array,default:()=>[]}},emits:["reveal"],setup(e,{emit:t}){const o=()=>t("reveal");return()=>l(s,{id:e.id,sensitivity:e.sensitivities,onReveal:o})}}),G={title:"Components/VSafetyWall",component:i,argTypes:{sensitivities:{control:{type:"check"},options:n},onReveal:{action:"reveal"}},args:{sensitivities:[...n],id:"f9384235-b72e-4f1e-9b05-e1b116262a29"}},r={render:e=>({components:{VSafetyWallWrapper:i},setup(){const t=()=>{console.log("Revealed")};return()=>l(i,{id:e.id,sensitivity:e.sensitivities,onReveal:t})}}),name:"default"};var a,p,m;r.parameters={...r.parameters,docs:{...(a=r.parameters)==null?void 0:a.docs,source:{originalSource:`{
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
