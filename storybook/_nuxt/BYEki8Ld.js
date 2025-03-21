import{h as l,d}from"./53SD24Bo.js";import{S as n}from"./Dy4Kknks.js";import{_ as s}from"./D-Mg0jyx.js";import"./DBIAFgjH.js";import"./Bji7sDXf.js";import"./BMTpeGZl.js";import"./CErlnN7q.js";import"./D_Aw-xVi.js";import"./qH-7fQ0Y.js";import"./7RO02bE1.js";import"./CPPXHlee.js";import"./DnIg5T83.js";import"./DJCDDsZ8.js";import"./B5GQZ6KW.js";import"./DQdiNp-F.js";import"./DiSpNEja.js";import"./BL5vD3y7.js";import"./CLb7Coka.js";import"./okj3qyDJ.js";import"./Bb2yh_vr.js";import"./BYpqqPRZ.js";import"./BRl0LMB0.js";import"./BNCCbueK.js";import"./DuKV0Hy2.js";import"./DhTbjJlp.js";import"./BwPl7lue.js";import"./CBc_U4V9.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="09d0864e-57e2-4a4f-a34e-1794775a7d00",e._sentryDebugIdIdentifier="sentry-dbid-09d0864e-57e2-4a4f-a34e-1794775a7d00")}catch{}})();const i=d({name:"VSafetyWallWrapper",components:{VSafetyWall:s},props:{id:{type:String,required:!0},sensitivities:{type:Array,default:()=>[]}},emits:["reveal"],setup(e,{emit:t}){const o=()=>t("reveal");return()=>l(s,{id:e.id,sensitivity:e.sensitivities,onReveal:o})}}),F={title:"Components/VSafetyWall",component:i,argTypes:{sensitivities:{control:{type:"check"},options:n},onReveal:{action:"reveal"}},args:{sensitivities:[...n],id:"f9384235-b72e-4f1e-9b05-e1b116262a29"}},r={render:e=>({components:{VSafetyWallWrapper:i},setup(){const t=()=>{console.log("Revealed")};return()=>l(i,{id:e.id,sensitivity:e.sensitivities,onReveal:t})}}),name:"default"};var a,p,m;r.parameters={...r.parameters,docs:{...(a=r.parameters)==null?void 0:a.docs,source:{originalSource:`{
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
