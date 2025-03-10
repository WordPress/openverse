import{h as l,d}from"./53SD24Bo.js";import{S as n}from"./D6RfD4r0.js";import{_ as s}from"./CuYMliIc.js";import"./RQxsyxdU.js";import"./BbcJJQG6.js";import"./f6gYKWT5.js";import"./BW6nfHgy.js";import"./BjsSTAr7.js";import"./Cai0IfA4.js";import"./7RO02bE1.js";import"./CGjrUY8T.js";import"./DXnxRZFx.js";import"./B2IxrC02.js";import"./CLVl6rL5.js";import"./C-ucudUc.js";import"./BALwooav.js";import"./CxEt8vcx.js";import"./BnJv8bNI.js";import"./okj3qyDJ.js";import"./B7ZxQ_gM.js";import"./CGdESDy3.js";import"./C4QhmNcb.js";import"./CxzE6WfI.js";import"./BsOxdBIg.js";import"./DhTbjJlp.js";import"./ByZ6H8Q9.js";import"./oAL5f6fw.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="09d0864e-57e2-4a4f-a34e-1794775a7d00",e._sentryDebugIdIdentifier="sentry-dbid-09d0864e-57e2-4a4f-a34e-1794775a7d00")}catch{}})();const i=d({name:"VSafetyWallWrapper",components:{VSafetyWall:s},props:{id:{type:String,required:!0},sensitivities:{type:Array,default:()=>[]}},emits:["reveal"],setup(e,{emit:t}){const o=()=>t("reveal");return()=>l(s,{id:e.id,sensitivity:e.sensitivities,onReveal:o})}}),F={title:"Components/VSafetyWall",component:i,argTypes:{sensitivities:{control:{type:"check"},options:n},onReveal:{action:"reveal"}},args:{sensitivities:[...n],id:"f9384235-b72e-4f1e-9b05-e1b116262a29"}},r={render:e=>({components:{VSafetyWallWrapper:i},setup(){const t=()=>{console.log("Revealed")};return()=>l(i,{id:e.id,sensitivity:e.sensitivities,onReveal:t})}}),name:"default"};var a,p,m;r.parameters={...r.parameters,docs:{...(a=r.parameters)==null?void 0:a.docs,source:{originalSource:`{
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
