import{h as S}from"./53SD24Bo.js";import{b as T}from"./BCWPXG3N.js";import{V as i}from"./Dzl5Fx40.js";import"./RQxsyxdU.js";import"./BjsSTAr7.js";import"./DYa50zxq.js";import"./DLCnOpdB.js";import"./BQrorSEU.js";import"./B06vE1PI.js";import"./RXhMJs7I.js";import"./DhTbjJlp.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="d0355eb7-8974-410b-990b-1215c8ad8452",e._sentryDebugIdIdentifier="sentry-dbid-d0355eb7-8974-410b-990b-1215c8ad8452")}catch{}})();const G={title:"Components/Audio track/Waveform",component:i,argTypes:{onSeeked:{action:"seeked"}},args:{audioId:"audio-1"}},a={render:e=>({components:{VWaveform:i},setup(){return()=>S(i,{class:"w-full h-30",...e})}})},I={currentTime:2,duration:10},c={...I,features:T},D={...c,peaks:[.5,1,.5,0,.5]},s={...a,name:"Upsampling",args:{...c,peaks:[.5,1,.5,0,.5,1,.5,0,.5]}},_=Array.from({length:1e3},(e,r)=>.5*Math.sin(r*2*Math.PI/500)+.5),n={...a,name:"Downsampling",args:{peaks:_,...c}},t={...a,name:"Background",args:{...D,style:{"--waveform-background-color":"#d7fcd4"}}},o={...a,name:"With blank space",args:{...D,usableFrac:.5}},m={...a,name:"Message",args:{message:"Hello, World!"}};var p,d,g;s.parameters={...s.parameters,docs:{...(p=s.parameters)==null?void 0:p.docs,source:{originalSource:`{
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
}`,...(f=(l=n.parameters)==null?void 0:l.docs)==null?void 0:f.source}}};var k,b,h;t.parameters={...t.parameters,docs:{...(k=t.parameters)==null?void 0:k.docs,source:{originalSource:`{
  ...Template,
  name: "Background",
  args: {
    ...timeArgsWithFeaturesAndPeaks,
    style: {
      "--waveform-background-color": "#d7fcd4"
    }
  }
}`,...(h=(b=t.parameters)==null?void 0:b.docs)==null?void 0:h.source}}};var W,w,y;o.parameters={...o.parameters,docs:{...(W=o.parameters)==null?void 0:W.docs,source:{originalSource:`{
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
