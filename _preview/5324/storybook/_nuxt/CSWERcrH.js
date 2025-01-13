import{A as Q,L as W,P as X,C as e,D as Z}from"./EYmIadoG.js";import{_ as E}from"./DLLG2T9S.js";import"./BQ2uyTwE.js";import{G as ee,h as se}from"./ueSFnAt6.js";import"./BS4Oynt6.js";import"./DHgysDkh.js";import"./BCbuITXb.js";import"./DLWVrS0P.js";import"./BKGw6EjD.js";import"./C_jCWbT6.js";import"./DzAq6MI-.js";import"./CG6WIkST.js";import"./BEqh9yyh.js";import"./cS2ccka-.js";import"./5wCrcqN-.js";import"./DSEYgdJX.js";import"./C4YS0AQy.js";import"./CFNrPCvG.js";import"./B_AFY9SJ.js";import"./DDGXuWLI.js";import"./DhTbjJlp.js";import"./rltOz0pP.js";import"./cXVshVQU.js";import"./DNI0JtzU.js";import"./A1b6Lb8y.js";import"./BQNGXNMh.js";import"../sb-preview/runtime.js";(function(){try{var s=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},a=new s.Error().stack;a&&(s._sentryDebugIds=s._sentryDebugIds||{},s._sentryDebugIds[a]="b4e7c4a2-f339-4574-a7c3-36953533e7ad",s._sentryDebugIdIdentifier="sentry-dbid-b4e7c4a2-f339-4574-a7c3-36953533e7ad")}catch{}})();const Ye={title:"Components/VMediaLicense",component:E,argTypes:{license:{options:Q,control:"select"},licenseVersion:{options:W,control:"select"}}},n={render:s=>({components:{VMediaLicense:E},setup(){const a=ee(()=>`https://creativecommons.org/licenses/${s.license}/${s.licenseVersion}/`);return()=>se(E,{...s,licenseUrl:a.value})}})},o={...n,name:"Default",inline:!1,args:{license:Q[0],licenseVersion:W[0]}},c={...n,name:"PDM",args:{license:X[0],licenseVersion:"1.0"}},i={...n,name:"CC0",args:{license:X[1],licenseVersion:"1.0"}},r=s=>`CC ${s.toUpperCase()}`,t={...n,name:r(e[0]),args:{license:e[0],licenseVersion:"4.0"}},m={...n,name:r(e[1]),args:{license:e[1],licenseVersion:"4.0"}},C={...n,name:r(e[2]),args:{license:e[2],licenseVersion:"4.0"}},p={...n,name:r(e[3]),args:{license:e[3],licenseVersion:"4.0"}},l={...n,name:r(e[4]),args:{license:e[4],licenseVersion:"4.0"}},S={...n,name:r(e[5]),args:{license:e[5],licenseVersion:"4.0"}},_={...n,name:"CC Sampling+",args:{license:Z[1],licenseVersion:"1.0"}},d={...n,name:"CC NC-Sampling+",args:{license:Z[0],licenseVersion:"1.0"}};var g,u,N;o.parameters={...o.parameters,docs:{...(g=o.parameters)==null?void 0:g.docs,source:{originalSource:`{
  ...Template,
  name: "Default",
  inline: false,
  args: {
    license: ALL_LICENSES[0],
    licenseVersion: LICENSE_VERSIONS[0]
  }
}`,...(N=(u=o.parameters)==null?void 0:u.docs)==null?void 0:N.source}}};var L,I,V;c.parameters={...c.parameters,docs:{...(L=c.parameters)==null?void 0:L.docs,source:{originalSource:`{
  ...Template,
  name: "PDM",
  args: {
    license: PUBLIC_DOMAIN_MARKS[0],
    licenseVersion: "1.0"
  }
}`,...(V=(I=c.parameters)==null?void 0:I.docs)==null?void 0:V.source}}};var D,f,A;i.parameters={...i.parameters,docs:{...(D=i.parameters)==null?void 0:D.docs,source:{originalSource:`{
  ...Template,
  name: "CC0",
  args: {
    license: PUBLIC_DOMAIN_MARKS[1],
    licenseVersion: "1.0"
  }
}`,...(A=(f=i.parameters)==null?void 0:f.docs)==null?void 0:A.source}}};var M,T,B;t.parameters={...t.parameters,docs:{...(M=t.parameters)==null?void 0:M.docs,source:{originalSource:`{
  ...Template,
  name: getLicenseName(CC_LICENSES[0]),
  args: {
    license: CC_LICENSES[0],
    licenseVersion: "4.0"
  }
}`,...(B=(T=t.parameters)==null?void 0:T.docs)==null?void 0:B.source}}};var P,Y,y;m.parameters={...m.parameters,docs:{...(P=m.parameters)==null?void 0:P.docs,source:{originalSource:`{
  ...Template,
  name: getLicenseName(CC_LICENSES[1]),
  args: {
    license: CC_LICENSES[1],
    licenseVersion: "4.0"
  }
}`,...(y=(Y=m.parameters)==null?void 0:Y.docs)==null?void 0:y.source}}};var b,R,O;C.parameters={...C.parameters,docs:{...(b=C.parameters)==null?void 0:b.docs,source:{originalSource:`{
  ...Template,
  name: getLicenseName(CC_LICENSES[2]),
  args: {
    license: CC_LICENSES[2],
    licenseVersion: "4.0"
  }
}`,...(O=(R=C.parameters)==null?void 0:R.docs)==null?void 0:O.source}}};var U,w,G;p.parameters={...p.parameters,docs:{...(U=p.parameters)==null?void 0:U.docs,source:{originalSource:`{
  ...Template,
  name: getLicenseName(CC_LICENSES[3]),
  args: {
    license: CC_LICENSES[3],
    licenseVersion: "4.0"
  }
}`,...(G=(w=p.parameters)==null?void 0:w.docs)==null?void 0:G.source}}};var h,v,K;l.parameters={...l.parameters,docs:{...(h=l.parameters)==null?void 0:h.docs,source:{originalSource:`{
  ...Template,
  name: getLicenseName(CC_LICENSES[4]),
  args: {
    license: CC_LICENSES[4],
    licenseVersion: "4.0"
  }
}`,...(K=(v=l.parameters)==null?void 0:v.docs)==null?void 0:K.source}}};var $,x,k;S.parameters={...S.parameters,docs:{...($=S.parameters)==null?void 0:$.docs,source:{originalSource:`{
  ...Template,
  name: getLicenseName(CC_LICENSES[5]),
  args: {
    license: CC_LICENSES[5],
    licenseVersion: "4.0"
  }
}`,...(k=(x=S.parameters)==null?void 0:x.docs)==null?void 0:k.source}}};var j,q,z;_.parameters={..._.parameters,docs:{...(j=_.parameters)==null?void 0:j.docs,source:{originalSource:`{
  ...Template,
  name: "CC Sampling+",
  args: {
    license: DEPRECATED_CC_LICENSES[1],
    licenseVersion: "1.0"
  }
}`,...(z=(q=_.parameters)==null?void 0:q.docs)==null?void 0:z.source}}};var F,H,J;d.parameters={...d.parameters,docs:{...(F=d.parameters)==null?void 0:F.docs,source:{originalSource:`{
  ...Template,
  name: "CC NC-Sampling+",
  args: {
    license: DEPRECATED_CC_LICENSES[0],
    licenseVersion: "1.0"
  }
}`,...(J=(H=d.parameters)==null?void 0:H.docs)==null?void 0:J.source}}};const ye=["Default","PDM","CC0","CC_BY","CC_BY_SA","CC_BY_ND","CC_BY_NC","CC_BY_NC_SA","CC_BY_NC_ND","SAMPLING","NC_SAMPLING"];export{i as CC0,t as CC_BY,p as CC_BY_NC,S as CC_BY_NC_ND,l as CC_BY_NC_SA,C as CC_BY_ND,m as CC_BY_SA,o as Default,d as NC_SAMPLING,c as PDM,_ as SAMPLING,ye as __namedExportsOrder,Ye as default};
