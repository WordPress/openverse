import{h as S}from"./DmrXErv4.js";import{b as T}from"./CJgmNVTT.js";import{V as c}from"./B3BXBp7S.js";import"./Cre_5D1H.js";import"./DFZUF_34.js";import"./CDE4LuQ1.js";import"./D5Za6x0E.js";import"./Dx-3nI8A.js";import"./CJ7FTku9.js";import"./CTAy5_it.js";import"./DhTbjJlp.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="f136ace3-632c-4877-adfe-58ca0447fd04",e._sentryDebugIdIdentifier="sentry-dbid-f136ace3-632c-4877-adfe-58ca0447fd04")}catch{}})();const G={title:"Components/Audio track/Waveform",component:c,argTypes:{onSeeked:{action:"seeked"}},args:{audioId:"audio-1"}},a={render:e=>({components:{VWaveform:c},setup(){return()=>S(c,{class:"w-full h-30",...e})}})},I={currentTime:2,duration:10},i={...I,features:T},D={...i,peaks:[.5,1,.5,0,.5]},s={...a,name:"Upsampling",args:{...i,peaks:[.5,1,.5,0,.5,1,.5,0,.5]}},_=Array.from({length:1e3},(e,r)=>.5*Math.sin(r*2*Math.PI/500)+.5),n={...a,name:"Downsampling",args:{peaks:_,...i}},t={...a,name:"Background",args:{...D,style:{"--waveform-background-color":"#d7fcd4"}}},o={...a,name:"With blank space",args:{...D,usableFrac:.5}},m={...a,name:"Message",args:{message:"Hello, World!"}};var p,d,g;s.parameters={...s.parameters,docs:{...(p=s.parameters)==null?void 0:p.docs,source:{originalSource:`{
  ...Template,
  name: "Upsampling",
  // triangular wave with 9 points
  args: {
    ...timeArgsWithFeatures,
    peaks: [0.5, 1, 0.5, 0, 0.5, 1, 0.5, 0, 0.5]
  }
}`,...(g=(d=s.parameters)==null?void 0:d.docs)==null?void 0:g.source}}};var u,l,f;n.parameters={...n.parameters,docs:{...(u=n.parameters)==null?void 0:u.docs,source:{originalSource:`{
  ...Template,
  name: "Downsampling",
  args: {
    peaks: sineWaveWith1000Points,
    ...timeArgsWithFeatures
  }
}`,...(f=(l=n.parameters)==null?void 0:l.docs)==null?void 0:f.source}}};var k,h,W;t.parameters={...t.parameters,docs:{...(k=t.parameters)==null?void 0:k.docs,source:{originalSource:`{
  ...Template,
  name: "Background",
  args: {
    ...timeArgsWithFeaturesAndPeaks,
    style: {
      "--waveform-background-color": "#d7fcd4"
    }
  }
}`,...(W=(h=t.parameters)==null?void 0:h.docs)==null?void 0:W.source}}};var b,w,y;o.parameters={...o.parameters,docs:{...(b=o.parameters)==null?void 0:b.docs,source:{originalSource:`{
  ...Template,
  name: "With blank space",
  args: {
    ...timeArgsWithFeaturesAndPeaks,
    usableFrac: 0.5
  }
}`,...(y=(w=o.parameters)==null?void 0:w.docs)==null?void 0:y.source}}};var A,F,v;m.parameters={...m.parameters,docs:{...(A=m.parameters)==null?void 0:A.docs,source:{originalSource:`{
  ...Template,
  name: "Message",
  args: {
    message: "Hello, World!"
  }
}`,...(v=(F=m.parameters)==null?void 0:F.docs)==null?void 0:v.source}}};const J=["Upsampling","Downsampling","Background","WithBlankSpace","Message"];export{t as Background,n as Downsampling,m as Message,s as Upsampling,o as WithBlankSpace,J as __namedExportsOrder,G as default};
