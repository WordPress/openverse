import{h as l,d}from"./DwwldUEF.js";import{S as n}from"./Ds_kB4O7.js";import{_ as s}from"./DmgBhuh4.js";import"./CWoQmekT.js";import"./Z8zkSHZ1.js";import"./CAa63J2U.js";import"./BAdCBbtP.js";import"./Dl1S6mqo.js";import"./TLA9Fm80.js";import"./Ck0CgHQL.js";import"./aHnQ5-ra.js";import"./ghAvikQd.js";import"./Bkc2CSET.js";import"./D8qJDlnG.js";import"./Cyc9srVp.js";import"./VcnMPoS3.js";import"./I6oWuQE1.js";import"./C8BbUAkk.js";import"./DzAq6MI-.js";import"./DqyB4W5h.js";import"./BtS8wA1z.js";import"./tAHCZdDM.js";import"./DoSYsHAz.js";import"./aezMCrU2.js";import"./DhTbjJlp.js";import"./Dhs1Or-2.js";import"./CUvT7aun.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="09d0864e-57e2-4a4f-a34e-1794775a7d00",e._sentryDebugIdIdentifier="sentry-dbid-09d0864e-57e2-4a4f-a34e-1794775a7d00")}catch{}})();const i=d({name:"VSafetyWallWrapper",components:{VSafetyWall:s},props:{id:{type:String,required:!0},sensitivities:{type:Array,default:()=>[]}},emits:["reveal"],setup(e,{emit:t}){const o=()=>t("reveal");return()=>l(s,{id:e.id,sensitivity:e.sensitivities,onReveal:o})}}),F={title:"Components/VSafetyWall",component:i,argTypes:{sensitivities:{control:{type:"check"},options:n},onReveal:{action:"reveal"}},args:{sensitivities:[...n],id:"f9384235-b72e-4f1e-9b05-e1b116262a29"}},r={render:e=>({components:{VSafetyWallWrapper:i},setup(){const t=()=>{console.log("Revealed")};return()=>l(i,{id:e.id,sensitivity:e.sensitivities,onReveal:t})}}),name:"default"};var a,p,m;r.parameters={...r.parameters,docs:{...(a=r.parameters)==null?void 0:a.docs,source:{originalSource:`{
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
