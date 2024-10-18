import{b as B}from"./BS9R2VWD.js";import{V as t}from"./DtGhSdeD.js";import{h as M}from"./lnpB3OcH.js";import"./DKepsN1e.js";import"./BSEdKPgk.js";import"./RevM6cLn.js";import"./BsSU7JKo.js";import"./Dt-H8hG_.js";import"./DlAUqK2U.js";const O={title:"Components/Audio track/Waveform",component:t,argTypes:{onSeeked:{action:"seeked"}},args:{audioId:"audio-1"}},e={render:c=>({components:{VWaveform:t},setup(){return()=>M(t,{class:"w-full h-30",...c})}})},P={currentTime:2,duration:10},m={...P,features:B},b={...m,peaks:[.5,1,.5,0,.5]},a={...e,name:"Upsampling",args:{...m,peaks:[.5,1,.5,0,.5,1,.5,0,.5]}},y=Array.from({length:1e3},(c,v)=>.5*Math.sin(v*2*Math.PI/500)+.5),s={...e,name:"Downsampling",args:{peaks:y,...m}},r={...e,name:"Background",args:{...b,style:{"--waveform-background-color":"#d7fcd4"}}},n={...e,name:"With blank space",args:{...b,usableFrac:.5}},o={...e,name:"Message",args:{message:"Hello, World!"}};var p,i,g;a.parameters={...a.parameters,docs:{...(p=a.parameters)==null?void 0:p.docs,source:{originalSource:`{
  ...Template,
  name: "Upsampling",
  // triangular wave with 9 points
  args: {
    ...timeArgsWithFeatures,
    peaks: [0.5, 1, 0.5, 0, 0.5, 1, 0.5, 0, 0.5]
  }
}`,...(g=(i=a.parameters)==null?void 0:i.docs)==null?void 0:g.source}}};var d,l,u;s.parameters={...s.parameters,docs:{...(d=s.parameters)==null?void 0:d.docs,source:{originalSource:`{
  ...Template,
  name: "Downsampling",
  args: {
    peaks: sineWaveWith1000Points,
    ...timeArgsWithFeatures
  }
}`,...(u=(l=s.parameters)==null?void 0:l.docs)==null?void 0:u.source}}};var k,h,W;r.parameters={...r.parameters,docs:{...(k=r.parameters)==null?void 0:k.docs,source:{originalSource:`{
  ...Template,
  name: "Background",
  args: {
    ...timeArgsWithFeaturesAndPeaks,
    style: {
      "--waveform-background-color": "#d7fcd4"
    }
  }
}`,...(W=(h=r.parameters)==null?void 0:h.docs)==null?void 0:W.source}}};var f,A,w;n.parameters={...n.parameters,docs:{...(f=n.parameters)==null?void 0:f.docs,source:{originalSource:`{
  ...Template,
  name: "With blank space",
  args: {
    ...timeArgsWithFeaturesAndPeaks,
    usableFrac: 0.5
  }
}`,...(w=(A=n.parameters)==null?void 0:A.docs)==null?void 0:w.source}}};var F,S,T;o.parameters={...o.parameters,docs:{...(F=o.parameters)==null?void 0:F.docs,source:{originalSource:`{
  ...Template,
  name: "Message",
  args: {
    message: "Hello, World!"
  }
}`,...(T=(S=o.parameters)==null?void 0:S.docs)==null?void 0:T.source}}};const j=["Upsampling","Downsampling","Background","WithBlankSpace","Message"];export{r as Background,s as Downsampling,o as Message,a as Upsampling,n as WithBlankSpace,j as __namedExportsOrder,O as default};
