import{A as Q,L as W,P as X,C as e,D as Z}from"./C7lp-ITr.js";import{_ as E}from"./Bv43ZfmE.js";import"./D6xGyQxu.js";import{C as ee,h as se}from"./Bf-AzR54.js";import"./BeomeOwa.js";import"./Tu1w6jvB.js";import"./DxaI9FRm.js";import"./BQ1PXazq.js";import"./BnJZTjE_.js";import"./G0IPDLoE.js";import"./DzAq6MI-.js";import"./DZIrc5my.js";import"./Lri8daXJ.js";import"./B06Wl6je.js";import"./eAGCzEdq.js";import"./CRElLIkf.js";import"./DBWmBUzF.js";import"./DmNhhvCU.js";import"./CO4aZKIX.js";import"./p8nc5Li4.js";import"./DhTbjJlp.js";import"./FADBYOvo.js";import"./BkbAmEqc.js";import"./D3fY7LA9.js";import"./EvZx83Uz.js";import"../sb-preview/runtime.js";(function(){try{var s=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},a=new s.Error().stack;a&&(s._sentryDebugIds=s._sentryDebugIds||{},s._sentryDebugIds[a]="a69bb130-97c0-4d2c-8721-e0735c785b4b",s._sentryDebugIdIdentifier="sentry-dbid-a69bb130-97c0-4d2c-8721-e0735c785b4b")}catch{}})();const Be={title:"Components/VMediaLicense",component:E,argTypes:{license:{options:Q,control:"select"},licenseVersion:{options:W,control:"select"}}},n={render:s=>({components:{VMediaLicense:E},setup(){const a=ee(()=>`https://creativecommons.org/licenses/${s.license}/${s.licenseVersion}/`);return()=>se(E,{...s,licenseUrl:a.value})}})},o={...n,name:"Default",inline:!1,args:{license:Q[0],licenseVersion:W[0]}},c={...n,name:"PDM",args:{license:X[0],licenseVersion:"1.0"}},i={...n,name:"CC0",args:{license:X[1],licenseVersion:"1.0"}},r=s=>`CC ${s.toUpperCase()}`,t={...n,name:r(e[0]),args:{license:e[0],licenseVersion:"4.0"}},m={...n,name:r(e[1]),args:{license:e[1],licenseVersion:"4.0"}},C={...n,name:r(e[2]),args:{license:e[2],licenseVersion:"4.0"}},p={...n,name:r(e[3]),args:{license:e[3],licenseVersion:"4.0"}},l={...n,name:r(e[4]),args:{license:e[4],licenseVersion:"4.0"}},S={...n,name:r(e[5]),args:{license:e[5],licenseVersion:"4.0"}},_={...n,name:"CC Sampling+",args:{license:Z[1],licenseVersion:"1.0"}},d={...n,name:"CC NC-Sampling+",args:{license:Z[0],licenseVersion:"1.0"}};var g,u,N;o.parameters={...o.parameters,docs:{...(g=o.parameters)==null?void 0:g.docs,source:{originalSource:`{
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
}`,...(A=(f=i.parameters)==null?void 0:f.docs)==null?void 0:A.source}}};var M,T,b;t.parameters={...t.parameters,docs:{...(M=t.parameters)==null?void 0:M.docs,source:{originalSource:`{
  ...Template,
  name: getLicenseName(CC_LICENSES[0]),
  args: {
    license: CC_LICENSES[0],
    licenseVersion: "4.0"
  }
}`,...(b=(T=t.parameters)==null?void 0:T.docs)==null?void 0:b.source}}};var B,P,Y;m.parameters={...m.parameters,docs:{...(B=m.parameters)==null?void 0:B.docs,source:{originalSource:`{
  ...Template,
  name: getLicenseName(CC_LICENSES[1]),
  args: {
    license: CC_LICENSES[1],
    licenseVersion: "4.0"
  }
}`,...(Y=(P=m.parameters)==null?void 0:P.docs)==null?void 0:Y.source}}};var y,R,O;C.parameters={...C.parameters,docs:{...(y=C.parameters)==null?void 0:y.docs,source:{originalSource:`{
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
}`,...(J=(H=d.parameters)==null?void 0:H.docs)==null?void 0:J.source}}};const Pe=["Default","PDM","CC0","CC_BY","CC_BY_SA","CC_BY_ND","CC_BY_NC","CC_BY_NC_SA","CC_BY_NC_ND","SAMPLING","NC_SAMPLING"];export{i as CC0,t as CC_BY,p as CC_BY_NC,S as CC_BY_NC_ND,l as CC_BY_NC_SA,C as CC_BY_ND,m as CC_BY_SA,o as Default,d as NC_SAMPLING,c as PDM,_ as SAMPLING,Pe as __namedExportsOrder,Be as default};
