import{u as f}from"./R-F224MX.js";import{a as h}from"./DTU7yJca.js";import{_ as s}from"./-3I6T1aZ.js";import{h as T}from"./-WkxctKM.js";import"./D-XGaJuf.js";import"./C36Bf8YV.js";import"./8bxaQBfd.js";import"./DNZ0QEaN.js";import"./CFMQYC2y.js";import"./BLIMiQvM.js";import"./CVtkxrq9.js";import"./Dt-H8hG_.js";import"./CTON8dBl.js";import"./CRWjC3CT.js";import"./Cpj98o6Y.js";import"./Ci7G4jyV.js";import"./HGGXJyB7.js";import"./D0ww02ZN.js";import"./Xs_VBmP5.js";import"./BKKKF4W5.js";import"./BnDRGrsR.js";import"./CVV9gpzL.js";import"./CuPsdpTl.js";import"./DlAUqK2U.js";import"./wQpWZeBh.js";import"./CmiN-34A.js";import"./BOX21o1p.js";const Y={title:"Components/VExternalSourceList",component:s},a=b=>({components:{VExternalSourceList:s},setup(){return f().toggleFeature("additional_search_types","on"),h().setSearchType(b.type),()=>T(s,{"search-term":"cat"})}}),e={render:a.bind({}),name:"Images",args:{type:"image"}},r={render:a.bind({}),name:"Audio",args:{type:"audio"}},o={render:a.bind({}),name:"Video",args:{type:"video"}},t={render:a.bind({}),name:"3D models",args:{type:"model-3d"}};var m,n,p;e.parameters={...e.parameters,docs:{...(m=e.parameters)==null?void 0:m.docs,source:{originalSource:`{
  render: Template.bind({}),
  name: "Images",
  args: {
    type: "image"
  }
}`,...(p=(n=e.parameters)==null?void 0:n.docs)==null?void 0:p.source}}};var i,d,c;r.parameters={...r.parameters,docs:{...(i=r.parameters)==null?void 0:i.docs,source:{originalSource:`{
  render: Template.bind({}),
  name: "Audio",
  args: {
    type: "audio"
  }
}`,...(c=(d=r.parameters)==null?void 0:d.docs)==null?void 0:c.source}}};var u,l,g;o.parameters={...o.parameters,docs:{...(u=o.parameters)==null?void 0:u.docs,source:{originalSource:`{
  render: Template.bind({}),
  name: "Video",
  args: {
    type: "video"
  }
}`,...(g=(l=o.parameters)==null?void 0:l.docs)==null?void 0:g.source}}};var S,y,_;t.parameters={...t.parameters,docs:{...(S=t.parameters)==null?void 0:S.docs,source:{originalSource:`{
  render: Template.bind({}),
  name: "3D models",
  args: {
    type: "model-3d"
  }
}`,...(_=(y=t.parameters)==null?void 0:y.docs)==null?void 0:_.source}}};const Z=["Images","Audio","Video","Model_3D"];export{r as Audio,e as Images,t as Model_3D,o as Video,Z as __namedExportsOrder,Y as default};
