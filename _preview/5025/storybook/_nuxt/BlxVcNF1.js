import{S as o}from"./PgLs4BFy.js";import{_ as n}from"./CimQOpfe.js";import{h as m,d as c}from"./lnpB3OcH.js";import"./BNurbrIm.js";import"./BInFDkJi.js";import"./D0ww02ZN.js";import"./CRWjC3CT.js";import"./wqDFrKMd.js";import"./DToSwJe0.js";import"./CVtkxrq9.js";import"./CoPWYLvr.js";import"./BvLt3-_D.js";import"./CFMQYC2y.js";import"./Dt-H8hG_.js";import"./Xs_VBmP5.js";import"./BJ-KpVIG.js";import"./CTON8dBl.js";import"./Cpj98o6Y.js";import"./Ci7G4jyV.js";import"./CtE17snF.js";import"./D-c0xjtQ.js";import"./ZjNmaQpL.js";import"./CuPsdpTl.js";import"./DlAUqK2U.js";import"./DuVMw8T-.js";import"./BOX21o1p.js";const r=c({name:"VSafetyWallWrapper",components:{VSafetyWall:n},props:{id:{type:String,required:!0},sensitivities:{type:Array,default:()=>[]}},emits:["reveal"],setup(e,{emit:i}){const l=()=>i("reveal");return()=>m(n,{id:e.id,sensitivity:e.sensitivities,onReveal:l})}}),z={title:"Components/VSafetyWall",component:r,argTypes:{sensitivities:{control:{type:"check"},options:o},onReveal:{action:"reveal"}},args:{sensitivities:[...o],id:"f9384235-b72e-4f1e-9b05-e1b116262a29"}},t={render:e=>({components:{VSafetyWallWrapper:r},setup(){const i=()=>{console.log("Revealed")};return()=>m(r,{id:e.id,sensitivity:e.sensitivities,onReveal:i})}}),name:"default"};var s,a,p;t.parameters={...t.parameters,docs:{...(s=t.parameters)==null?void 0:s.docs,source:{originalSource:`{
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
}`,...(p=(a=t.parameters)==null?void 0:a.docs)==null?void 0:p.source}}};const B=["Default"];export{t as Default,B as __namedExportsOrder,z as default};
