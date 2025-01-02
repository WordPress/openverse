import{S as n}from"./xNdBFmJU.js";import{_ as a}from"./BLMgRQzI.js";import"./DUksCy1Q.js";import{h as l,d}from"./Bf-AzR54.js";import"./C91c9mPJ.js";import"./DqF6eGgl.js";import"./Ce-pb_5E.js";import"./CH1X1jge.js";import"./DekjSk5G.js";import"./B06Wl6je.js";import"./BkYjW3Tf.js";import"./Drofs-2p.js";import"./-xUPu9Rx.js";import"./y8WIPfCZ.js";import"./-W0rxRVk.js";import"./CQEj5Ugn.js";import"./DC3f6ECh.js";import"./qkf-DtgY.js";import"./DzAq6MI-.js";import"./Cf91XFr0.js";import"./CvkTs5vB.js";import"./8Pdn1Bl1.js";import"./CAhZsXLM.js";import"./BEmSFkVT.js";import"./DhTbjJlp.js";import"./DIrLFUJi.js";import"./CGo6q8cg.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="8d1e416c-d272-46a9-86ea-a9a9427055b1",e._sentryDebugIdIdentifier="sentry-dbid-8d1e416c-d272-46a9-86ea-a9a9427055b1")}catch{}})();const i=d({name:"VSafetyWallWrapper",components:{VSafetyWall:a},props:{id:{type:String,required:!0},sensitivities:{type:Array,default:()=>[]}},emits:["reveal"],setup(e,{emit:t}){const o=()=>t("reveal");return()=>l(a,{id:e.id,sensitivity:e.sensitivities,onReveal:o})}}),F={title:"Components/VSafetyWall",component:i,argTypes:{sensitivities:{control:{type:"check"},options:n},onReveal:{action:"reveal"}},args:{sensitivities:[...n],id:"f9384235-b72e-4f1e-9b05-e1b116262a29"}},r={render:e=>({components:{VSafetyWallWrapper:i},setup(){const t=()=>{console.log("Revealed")};return()=>l(i,{id:e.id,sensitivity:e.sensitivities,onReveal:t})}}),name:"default"};var s,p,m;r.parameters={...r.parameters,docs:{...(s=r.parameters)==null?void 0:s.docs,source:{originalSource:`{
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
