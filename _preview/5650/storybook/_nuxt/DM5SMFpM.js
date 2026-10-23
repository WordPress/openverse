import{c as ee,h as se}from"./DmrXErv4.js";import{P as Q,C as e,L as W,A as X,D as Z}from"./D7WD_DXd.js";import{_ as E}from"./B9vyPqKb.js";import"./Cre_5D1H.js";import"./CDy5EAa_.js";import"./C7sHCGoX.js";import"./laSThfNN.js";import"./BAdK41rD.js";import"./P7ZX4TMp.js";import"./CT8Zrxvs.js";import"./DzAq6MI-.js";import"./Dt27wNGp.js";import"./CnhD0xjG.js";import"./BxtqxG2r.js";import"./CEG4L8Wc.js";import"./B3KNKrKa.js";import"./B_dsH32H.js";import"./rMKLwKwR.js";import"./Dv0Nl23j.js";import"./Bn7RUpRV.js";import"./DhTbjJlp.js";import"./D5Za6x0E.js";import"./Dx-3nI8A.js";import"./CJ7FTku9.js";import"./DWRfakdt.js";import"./CCN4kZnP.js";import"./OMXwMIS8.js";import"../sb-preview/runtime.js";(function(){try{var s=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},a=new s.Error().stack;a&&(s._sentryDebugIds=s._sentryDebugIds||{},s._sentryDebugIds[a]="62997548-fa65-4773-8ce0-182270360397",s._sentryDebugIdIdentifier="sentry-dbid-62997548-fa65-4773-8ce0-182270360397")}catch{}})();const ye={title:"Components/VMediaLicense",component:E,argTypes:{license:{options:X,control:"select"},licenseVersion:{options:W,control:"select"}}},n={render:s=>({components:{VMediaLicense:E},setup(){const a=ee(()=>`https://creativecommons.org/licenses/${s.license}/${s.licenseVersion}/`);return()=>se(E,{...s,licenseUrl:a.value})}})},o={...n,name:"Default",inline:!1,args:{license:X[0],licenseVersion:W[0]}},c={...n,name:"PDM",args:{license:Q[0],licenseVersion:"1.0"}},i={...n,name:"CC0",args:{license:Q[1],licenseVersion:"1.0"}},r=s=>`CC ${s.toUpperCase()}`,t={...n,name:r(e[0]),args:{license:e[0],licenseVersion:"4.0"}},m={...n,name:r(e[1]),args:{license:e[1],licenseVersion:"4.0"}},C={...n,name:r(e[2]),args:{license:e[2],licenseVersion:"4.0"}},p={...n,name:r(e[3]),args:{license:e[3],licenseVersion:"4.0"}},l={...n,name:r(e[4]),args:{license:e[4],licenseVersion:"4.0"}},S={...n,name:r(e[5]),args:{license:e[5],licenseVersion:"4.0"}},_={...n,name:"CC Sampling+",args:{license:Z[1],licenseVersion:"1.0"}},d={...n,name:"CC NC-Sampling+",args:{license:Z[0],licenseVersion:"1.0"}};var g,u,N;o.parameters={...o.parameters,docs:{...(g=o.parameters)==null?void 0:g.docs,source:{originalSource:`{
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
}`,...(y=(Y=m.parameters)==null?void 0:Y.docs)==null?void 0:y.source}}};var R,b,O;C.parameters={...C.parameters,docs:{...(R=C.parameters)==null?void 0:R.docs,source:{originalSource:`{
  ...Template,
  name: getLicenseName(CC_LICENSES[2]),
  args: {
    license: CC_LICENSES[2],
    licenseVersion: "4.0"
  }
}`,...(O=(b=C.parameters)==null?void 0:b.docs)==null?void 0:O.source}}};var U,w,G;p.parameters={...p.parameters,docs:{...(U=p.parameters)==null?void 0:U.docs,source:{originalSource:`{
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
}`,...(J=(H=d.parameters)==null?void 0:H.docs)==null?void 0:J.source}}};const Re=["Default","PDM","CC0","CC_BY","CC_BY_SA","CC_BY_ND","CC_BY_NC","CC_BY_NC_SA","CC_BY_NC_ND","SAMPLING","NC_SAMPLING"];export{i as CC0,t as CC_BY,p as CC_BY_NC,S as CC_BY_NC_ND,l as CC_BY_NC_SA,C as CC_BY_ND,m as CC_BY_SA,o as Default,d as NC_SAMPLING,c as PDM,_ as SAMPLING,Re as __namedExportsOrder,ye as default};
