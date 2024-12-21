import{W as g}from"./_AySTw1G.js";import{_ as r}from"./MKJd9PKB.js";import{V as c}from"./DRAbbxNl.js";import{h as e}from"./D21kBugn.js";import"./BMFse2nb.js";import"./DzUJZ0J9.js";import"./DEweiwTv.js";import"./CFMQYC2y.js";import"./DlAUqK2U.js";import"./BinJqSUb.js";import"./Ci7G4jyV.js";import"./D0ww02ZN.js";import"./NZ_iG7Tn.js";import"./J0SANkQt.js";import"./C66CHCZN.js";import"./yNK1ymcv.js";import"./KtaE-n0E.js";import"./DmWT6tLV.js";import"./JYtQN4fY.js";import"./CszWEYKx.js";import"./CVtkxrq9.js";import"./Cpw-XNzg.js";import"./DyBDyB1K.js";import"./C1YDwe8s.js";const H={title:"Components/VCheckbox",component:r,decorators:[g],args:{id:"default",name:"Code is Poetry",value:"codeIsPoetry",checked:!1,isSwitch:!1},argTypes:{onChange:{action:"change"}}},f={render:n=>({components:{VCheckbox:r},setup(){return()=>e(r,n,{default:()=>n.name})}})},t={...f,name:"Default"},o={...f,name:"Switch",args:{isSwitch:!0}},s={name:"License Checkbox",render:n=>({components:{VCheckbox:r,VLicense:c},setup(){return()=>e("fieldset",{},[e("legend",{},"License"),e(r,{...n,class:"mb-4"},[e(c,{license:"by-nc",class:"me-4"})])])}}),args:{id:"cc-by",name:"license",value:"cc-by",checked:!0}};var a,m,i;t.parameters={...t.parameters,docs:{...(a=t.parameters)==null?void 0:a.docs,source:{originalSource:`{
  ...Template,
  name: "Default"
}`,...(i=(m=t.parameters)==null?void 0:m.docs)==null?void 0:i.source}}};var p,l,d;o.parameters={...o.parameters,docs:{...(p=o.parameters)==null?void 0:p.docs,source:{originalSource:`{
  ...Template,
  name: "Switch",
  args: {
    isSwitch: true
  }
}`,...(d=(l=o.parameters)==null?void 0:l.docs)==null?void 0:d.source}}};var u,h,b;s.parameters={...s.parameters,docs:{...(u=s.parameters)==null?void 0:u.docs,source:{originalSource:`{
  name: "License Checkbox",
  render: args => ({
    components: {
      VCheckbox,
      VLicense
    },
    setup() {
      return () => h("fieldset", {}, [h("legend", {}, "License"), h(VCheckbox, {
        ...args,
        class: "mb-4"
      }, [h(VLicense, {
        license: "by-nc",
        class: "me-4"
      })])]);
    }
  }),
  args: {
    id: "cc-by",
    name: "license",
    value: "cc-by",
    checked: true
  }
}`,...(b=(h=s.parameters)==null?void 0:h.docs)==null?void 0:b.source}}};const J=["Default","Switch","LicenseCheckbox"];export{t as Default,s as LicenseCheckbox,o as Switch,J as __namedExportsOrder,H as default};
