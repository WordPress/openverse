import{S as n}from"./DIoPOIW-.js";import{_ as a}from"./bxeQZlrD.js";import"./DJiKieMK.js";import{h as l,d}from"./Bf-AzR54.js";import"./DP_WGbG6.js";import"./DHc3v09i.js";import"./Bny5abkt.js";import"./HRLWcGUV.js";import"./BHCnpuXR.js";import"./B06Wl6je.js";import"./l54NnjUF.js";import"./CeH6ebnn.js";import"./DCDaOnb6.js";import"./C-dE80hk.js";import"./CUsr6PUM.js";import"./qA--S04K.js";import"./XhmO_eME.js";import"./tw9gWovy.js";import"./DzAq6MI-.js";import"./Cyf2jyE0.js";import"./DcwCHNwG.js";import"./BgVAWI2R.js";import"./cGIRWP1M.js";import"./BAvHRt8K.js";import"./DhTbjJlp.js";import"./BtGsfS_x.js";import"./CdpvutFv.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="8d1e416c-d272-46a9-86ea-a9a9427055b1",e._sentryDebugIdIdentifier="sentry-dbid-8d1e416c-d272-46a9-86ea-a9a9427055b1")}catch{}})();const i=d({name:"VSafetyWallWrapper",components:{VSafetyWall:a},props:{id:{type:String,required:!0},sensitivities:{type:Array,default:()=>[]}},emits:["reveal"],setup(e,{emit:t}){const o=()=>t("reveal");return()=>l(a,{id:e.id,sensitivity:e.sensitivities,onReveal:o})}}),F={title:"Components/VSafetyWall",component:i,argTypes:{sensitivities:{control:{type:"check"},options:n},onReveal:{action:"reveal"}},args:{sensitivities:[...n],id:"f9384235-b72e-4f1e-9b05-e1b116262a29"}},r={render:e=>({components:{VSafetyWallWrapper:i},setup(){const t=()=>{console.log("Revealed")};return()=>l(i,{id:e.id,sensitivity:e.sensitivities,onReveal:t})}}),name:"default"};var s,p,m;r.parameters={...r.parameters,docs:{...(s=r.parameters)==null?void 0:s.docs,source:{originalSource:`{
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
