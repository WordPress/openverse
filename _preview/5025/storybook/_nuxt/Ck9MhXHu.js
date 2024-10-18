import{A as J,L as Q,P as W,C as e,D as X}from"./Ci7G4jyV.js";import{_ as E}from"./CdeBVJGP.js";import{C as ee,h as se}from"./lnpB3OcH.js";import"./DKepsN1e.js";import"./BSEdKPgk.js";import"./BNurbrIm.js";import"./Bnkvtx4f.js";import"./D0ww02ZN.js";import"./86gNHKjF.js";import"./DH-KChwL.js";import"./BsB6Edd_.js";import"./DToSwJe0.js";import"./CVtkxrq9.js";import"./BInFDkJi.js";import"./CoPWYLvr.js";import"./wqDFrKMd.js";import"./BvLt3-_D.js";import"./CFMQYC2y.js";import"./ZjNmaQpL.js";import"./CuPsdpTl.js";import"./DlAUqK2U.js";import"./CtE17snF.js";import"./D-c0xjtQ.js";const Me={title:"Components/VMediaLicense",component:E,argTypes:{license:{options:J,control:"select"},licenseVersion:{options:Q,control:"select"}}},s={render:r=>({components:{VMediaLicense:E},setup(){const Z=ee(()=>`https://creativecommons.org/licenses/${r.license}/${r.licenseVersion}/`);return()=>se(E,{...r,licenseUrl:Z.value})}})},a={...s,name:"Default",inline:!1,args:{license:J[0],licenseVersion:Q[0]}},o={...s,name:"PDM",args:{license:W[0],licenseVersion:"1.0"}},c={...s,name:"CC0",args:{license:W[1],licenseVersion:"1.0"}},n=r=>`CC ${r.toUpperCase()}`,i={...s,name:n(e[0]),args:{license:e[0],licenseVersion:"4.0"}},t={...s,name:n(e[1]),args:{license:e[1],licenseVersion:"4.0"}},m={...s,name:n(e[2]),args:{license:e[2],licenseVersion:"4.0"}},C={...s,name:n(e[3]),args:{license:e[3],licenseVersion:"4.0"}},p={...s,name:n(e[4]),args:{license:e[4],licenseVersion:"4.0"}},l={...s,name:n(e[5]),args:{license:e[5],licenseVersion:"4.0"}},S={...s,name:"CC Sampling+",args:{license:X[1],licenseVersion:"1.0"}},_={...s,name:"CC NC-Sampling+",args:{license:X[0],licenseVersion:"1.0"}};var N,g,u;a.parameters={...a.parameters,docs:{...(N=a.parameters)==null?void 0:N.docs,source:{originalSource:`{
  ...Template,
  name: "Default",
  inline: false,
  args: {
    license: ALL_LICENSES[0],
    licenseVersion: LICENSE_VERSIONS[0]
  }
}`,...(u=(g=a.parameters)==null?void 0:g.docs)==null?void 0:u.source}}};var L,d,I;o.parameters={...o.parameters,docs:{...(L=o.parameters)==null?void 0:L.docs,source:{originalSource:`{
  ...Template,
  name: "PDM",
  args: {
    license: PUBLIC_DOMAIN_MARKS[0],
    licenseVersion: "1.0"
  }
}`,...(I=(d=o.parameters)==null?void 0:d.docs)==null?void 0:I.source}}};var V,D,A;c.parameters={...c.parameters,docs:{...(V=c.parameters)==null?void 0:V.docs,source:{originalSource:`{
  ...Template,
  name: "CC0",
  args: {
    license: PUBLIC_DOMAIN_MARKS[1],
    licenseVersion: "1.0"
  }
}`,...(A=(D=c.parameters)==null?void 0:D.docs)==null?void 0:A.source}}};var M,T,B;i.parameters={...i.parameters,docs:{...(M=i.parameters)==null?void 0:M.docs,source:{originalSource:`{
  ...Template,
  name: getLicenseName(CC_LICENSES[0]),
  args: {
    license: CC_LICENSES[0],
    licenseVersion: "4.0"
  }
}`,...(B=(T=i.parameters)==null?void 0:T.docs)==null?void 0:B.source}}};var P,Y,f;t.parameters={...t.parameters,docs:{...(P=t.parameters)==null?void 0:P.docs,source:{originalSource:`{
  ...Template,
  name: getLicenseName(CC_LICENSES[1]),
  args: {
    license: CC_LICENSES[1],
    licenseVersion: "4.0"
  }
}`,...(f=(Y=t.parameters)==null?void 0:Y.docs)==null?void 0:f.source}}};var R,O,U;m.parameters={...m.parameters,docs:{...(R=m.parameters)==null?void 0:R.docs,source:{originalSource:`{
  ...Template,
  name: getLicenseName(CC_LICENSES[2]),
  args: {
    license: CC_LICENSES[2],
    licenseVersion: "4.0"
  }
}`,...(U=(O=m.parameters)==null?void 0:O.docs)==null?void 0:U.source}}};var G,K,$;C.parameters={...C.parameters,docs:{...(G=C.parameters)==null?void 0:G.docs,source:{originalSource:`{
  ...Template,
  name: getLicenseName(CC_LICENSES[3]),
  args: {
    license: CC_LICENSES[3],
    licenseVersion: "4.0"
  }
}`,...($=(K=C.parameters)==null?void 0:K.docs)==null?void 0:$.source}}};var h,v,x;p.parameters={...p.parameters,docs:{...(h=p.parameters)==null?void 0:h.docs,source:{originalSource:`{
  ...Template,
  name: getLicenseName(CC_LICENSES[4]),
  args: {
    license: CC_LICENSES[4],
    licenseVersion: "4.0"
  }
}`,...(x=(v=p.parameters)==null?void 0:v.docs)==null?void 0:x.source}}};var y,b,j;l.parameters={...l.parameters,docs:{...(y=l.parameters)==null?void 0:y.docs,source:{originalSource:`{
  ...Template,
  name: getLicenseName(CC_LICENSES[5]),
  args: {
    license: CC_LICENSES[5],
    licenseVersion: "4.0"
  }
}`,...(j=(b=l.parameters)==null?void 0:b.docs)==null?void 0:j.source}}};var k,q,w;S.parameters={...S.parameters,docs:{...(k=S.parameters)==null?void 0:k.docs,source:{originalSource:`{
  ...Template,
  name: "CC Sampling+",
  args: {
    license: DEPRECATED_CC_LICENSES[1],
    licenseVersion: "1.0"
  }
}`,...(w=(q=S.parameters)==null?void 0:q.docs)==null?void 0:w.source}}};var z,F,H;_.parameters={..._.parameters,docs:{...(z=_.parameters)==null?void 0:z.docs,source:{originalSource:`{
  ...Template,
  name: "CC NC-Sampling+",
  args: {
    license: DEPRECATED_CC_LICENSES[0],
    licenseVersion: "1.0"
  }
}`,...(H=(F=_.parameters)==null?void 0:F.docs)==null?void 0:H.source}}};const Te=["Default","PDM","CC0","CC_BY","CC_BY_SA","CC_BY_ND","CC_BY_NC","CC_BY_NC_SA","CC_BY_NC_ND","SAMPLING","NC_SAMPLING"];export{c as CC0,i as CC_BY,C as CC_BY_NC,l as CC_BY_NC_ND,p as CC_BY_NC_SA,m as CC_BY_ND,t as CC_BY_SA,a as Default,_ as NC_SAMPLING,o as PDM,S as SAMPLING,Te as __namedExportsOrder,Me as default};
