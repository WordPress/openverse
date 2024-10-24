import{V as n}from"./BHwUdJbU.js";import{I as y,h as e}from"./lnpB3OcH.js";import"./DlAUqK2U.js";const P={title:"Components/VInputField",component:n,argTypes:{"onUpdate:modelValue":{action:"update:modelValue"}},args:{fieldId:"field",labelText:"Label"}},d={render:a=>({components:{VInputField:n},setup(){return()=>e(n,{...a},{default:()=>e("span",{class:"whitespace-nowrap me-2"},"Extra info")})}})},t={...d,name:"Default",args:{value:"Text goes here"}},r={render:a=>({components:{VInputField:n},setup(){const m=y("Hello, World!"),w=p=>m.value=typeof p=="string"?p:"";return()=>e("div",{},e(n,{...a,modelValue:m.value,"onUpdate:modelValue":w},{default:()=>m.value}))}}),name:"v-model"},o={...d,name:"With placeholder",args:{placeholder:"Enter something here"}},s={...d,name:"With label text",args:{labelText:"Label:"}},l={render:a=>({components:{VInputField:n},setup(){return()=>e("div",{},[e("label",{for:"field"},"Label:"),e(n,{...a})])}}),name:"With custom label"},c={...d,name:"With connections",args:{connectionSides:["start","end"]}};var u,i,h;t.parameters={...t.parameters,docs:{...(u=t.parameters)==null?void 0:u.docs,source:{originalSource:`{
  ...Template,
  name: "Default",
  args: {
    value: "Text goes here"
  }
}`,...(h=(i=t.parameters)==null?void 0:i.docs)==null?void 0:h.source}}};var g,f,x;r.parameters={...r.parameters,docs:{...(g=r.parameters)==null?void 0:g.docs,source:{originalSource:`{
  render: args => ({
    components: {
      VInputField
    },
    setup() {
      const text = ref("Hello, World!");
      const updateText = (value: unknown) => text.value = typeof value === "string" ? value : "";
      return () => h("div", {}, h(VInputField, {
        ...args,
        modelValue: text.value,
        "onUpdate:modelValue": updateText
      }, {
        default: () => text.value
      }));
    }
  }),
  name: "v-model"
}`,...(x=(f=r.parameters)==null?void 0:f.docs)==null?void 0:x.source}}};var b,W,v;o.parameters={...o.parameters,docs:{...(b=o.parameters)==null?void 0:b.docs,source:{originalSource:`{
  ...Template,
  name: "With placeholder",
  args: {
    placeholder: "Enter something here"
  }
}`,...(v=(W=o.parameters)==null?void 0:W.docs)==null?void 0:v.source}}};var T,V,L;s.parameters={...s.parameters,docs:{...(T=s.parameters)==null?void 0:T.docs,source:{originalSource:`{
  ...Template,
  name: "With label text",
  args: {
    labelText: "Label:"
  }
}`,...(L=(V=s.parameters)==null?void 0:V.docs)==null?void 0:L.source}}};var I,S,F;l.parameters={...l.parameters,docs:{...(I=l.parameters)==null?void 0:I.docs,source:{originalSource:`{
  render: args => ({
    components: {
      VInputField
    },
    setup() {
      return () => h("div", {}, [h("label", {
        for: "field"
      }, "Label:"), h(VInputField, {
        ...args
      })]);
    }
  }),
  name: "With custom label"
}`,...(F=(S=l.parameters)==null?void 0:S.docs)==null?void 0:F.source}}};var C,D,E;c.parameters={...c.parameters,docs:{...(C=c.parameters)==null?void 0:C.docs,source:{originalSource:`{
  ...Template,
  name: "With connections",
  args: {
    connectionSides: ["start", "end"]
  }
}`,...(E=(D=c.parameters)==null?void 0:D.docs)==null?void 0:E.source}}};const _=["Default","VModel","WithPlaceholder","WithLabelText","WithCustomLabel","WithConnections"];export{t as Default,r as VModel,c as WithConnections,l as WithCustomLabel,s as WithLabelText,o as WithPlaceholder,_ as __namedExportsOrder,P as default};
