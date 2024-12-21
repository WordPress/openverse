import{S as n}from"./CSbO3l5S.js";import{_ as a}from"./BuLw-Arh.js";import"./Cb7Zuqx8.js";import{h as l,d}from"./Bf-AzR54.js";import"./BiC8Cn9J.js";import"./CMfearWB.js";import"./BVPzU1gS.js";import"./CX0YfO9m.js";import"./OXefpJAj.js";import"./B06Wl6je.js";import"./Dm2Vgud-.js";import"./CZvnpAZI.js";import"./Dy3_0OnD.js";import"./MEtS268D.js";import"./Bqz7oJe_.js";import"./CXyLtIA_.js";import"./D3mt7-LU.js";import"./CaHoH0jp.js";import"./DzAq6MI-.js";import"./D0sNZIq0.js";import"./LrXbMvc1.js";import"./53t0DvQJ.js";import"./4JVUVGS7.js";import"./BtGjuzI1.js";import"./DhTbjJlp.js";import"./Dbp9NDS0.js";import"./CaLJbFDg.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="8d1e416c-d272-46a9-86ea-a9a9427055b1",e._sentryDebugIdIdentifier="sentry-dbid-8d1e416c-d272-46a9-86ea-a9a9427055b1")}catch{}})();const i=d({name:"VSafetyWallWrapper",components:{VSafetyWall:a},props:{id:{type:String,required:!0},sensitivities:{type:Array,default:()=>[]}},emits:["reveal"],setup(e,{emit:t}){const o=()=>t("reveal");return()=>l(a,{id:e.id,sensitivity:e.sensitivities,onReveal:o})}}),F={title:"Components/VSafetyWall",component:i,argTypes:{sensitivities:{control:{type:"check"},options:n},onReveal:{action:"reveal"}},args:{sensitivities:[...n],id:"f9384235-b72e-4f1e-9b05-e1b116262a29"}},r={render:e=>({components:{VSafetyWallWrapper:i},setup(){const t=()=>{console.log("Revealed")};return()=>l(i,{id:e.id,sensitivity:e.sensitivities,onReveal:t})}}),name:"default"};var s,p,m;r.parameters={...r.parameters,docs:{...(s=r.parameters)==null?void 0:s.docs,source:{originalSource:`{
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
