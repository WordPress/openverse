import{h as l,d}from"./DmrXErv4.js";import{S as n}from"./-2B6Z20n.js";import{_ as s}from"./CN5qf_1m.js";import"./Ceavzuo-.js";import"./Dbo3V4Mp.js";import"./9mLNX8sN.js";import"./DNv5NVgs.js";import"./i2yG8VlY.js";import"./Dp2jPxn_.js";import"./BxtqxG2r.js";import"./Bp0tQXh7.js";import"./COQlapGP.js";import"./JU2JEH3o.js";import"./Dyqkukzd.js";import"./DoeNFUMW.js";import"./BS_ZT77X.js";import"./FWiT1Y5Q.js";import"./C_FySRQg.js";import"./DzAq6MI-.js";import"./CtkidDXQ.js";import"./CMZS2cOm.js";import"./BayljJpb.js";import"./Ck0gvfbg.js";import"./CdX5GYQk.js";import"./qy-jYTsH.js";import"./DhTbjJlp.js";import"./0xbGHjBU.js";import"./lCCmDL6e.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="9e5fcd08-1a90-44d9-83f6-972a51105ac9",e._sentryDebugIdIdentifier="sentry-dbid-9e5fcd08-1a90-44d9-83f6-972a51105ac9")}catch{}})();const i=d({name:"VSafetyWallWrapper",components:{VSafetyWall:s},props:{id:{type:String,required:!0},sensitivities:{type:Array,default:()=>[]}},emits:["reveal"],setup(e,{emit:t}){const o=()=>t("reveal");return()=>l(s,{id:e.id,sensitivity:e.sensitivities,onReveal:o})}}),G={title:"Components/VSafetyWall",component:i,argTypes:{sensitivities:{control:{type:"check"},options:n},onReveal:{action:"reveal"}},args:{sensitivities:[...n],id:"f9384235-b72e-4f1e-9b05-e1b116262a29"}},r={render:e=>({components:{VSafetyWallWrapper:i},setup(){const t=()=>{console.log("Revealed")};return()=>l(i,{id:e.id,sensitivity:e.sensitivities,onReveal:t})}}),name:"default"};var a,p,m;r.parameters={...r.parameters,docs:{...(a=r.parameters)==null?void 0:a.docs,source:{originalSource:`{
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
