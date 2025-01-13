import{S as n}from"./BKvBQNfv.js";import{_ as s}from"./C6aiYQH3.js";import"./BQ2uyTwE.js";import{h as m,d as l}from"./ueSFnAt6.js";import"./BKGw6EjD.js";import"./BUcLuzj5.js";import"./D9PGBJDx.js";import"./CxIz9G_3.js";import"./DSEYgdJX.js";import"./cS2ccka-.js";import"./EYmIadoG.js";import"./nu0uObuU.js";import"./CP2tuLu8.js";import"./BXlC2Afm.js";import"./DHgysDkh.js";import"./C4YS0AQy.js";import"./5wCrcqN-.js";import"./C_jCWbT6.js";import"./DzAq6MI-.js";import"./A1b6Lb8y.js";import"./BQNGXNMh.js";import"./DDGXuWLI.js";import"./CFNrPCvG.js";import"./B_AFY9SJ.js";import"./DhTbjJlp.js";import"./DKvPnfU5.js";import"./DI2Xpw6B.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="536dede7-b1fd-4b84-98fd-be4dfc8a23df",e._sentryDebugIdIdentifier="sentry-dbid-536dede7-b1fd-4b84-98fd-be4dfc8a23df")}catch{}})();const i=l({name:"VSafetyWallWrapper",components:{VSafetyWall:s},props:{id:{type:String,required:!0},sensitivities:{type:Array,default:()=>[]}},emits:["reveal"],setup(e,{emit:t}){const o=()=>t("reveal");return()=>m(s,{id:e.id,sensitivity:e.sensitivities,onReveal:o})}}),F={title:"Components/VSafetyWall",component:i,argTypes:{sensitivities:{control:{type:"check"},options:n},onReveal:{action:"reveal"}},args:{sensitivities:[...n],id:"f9384235-b72e-4f1e-9b05-e1b116262a29"}},r={render:e=>({components:{VSafetyWallWrapper:i},setup(){const t=()=>{console.log("Revealed")};return()=>m(i,{id:e.id,sensitivity:e.sensitivities,onReveal:t})}}),name:"default"};var a,p,d;r.parameters={...r.parameters,docs:{...(a=r.parameters)==null?void 0:a.docs,source:{originalSource:`{
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
}`,...(d=(p=r.parameters)==null?void 0:p.docs)==null?void 0:d.source}}};const G=["Default"];export{r as Default,G as __namedExportsOrder,F as default};
