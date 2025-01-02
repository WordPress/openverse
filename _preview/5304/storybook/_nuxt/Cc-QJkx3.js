import{V as t}from"./CVxoL6nj.js";import"./DJiKieMK.js";import{D as C,h as n}from"./Bf-AzR54.js";import"./DhTbjJlp.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},a=new e.Error().stack;a&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[a]="47cb76de-37b6-432e-8016-6496ec4e57f4",e._sentryDebugIdIdentifier="sentry-dbid-47cb76de-37b6-432e-8016-6496ec4e57f4")}catch{}})();const P={title:"Components/VInputField",component:t,argTypes:{"onUpdate:modelValue":{action:"update:modelValue"}},args:{fieldId:"field",labelText:"Label"}},u={render:e=>({components:{VInputField:t},setup(){return()=>n(t,{...e},{default:()=>n("span",{class:"whitespace-nowrap me-2"},"Extra info")})}})},r={...u,name:"Default",args:{value:"Text goes here"}},o={render:e=>({components:{VInputField:t},setup(){const a=C("Hello, World!"),p=i=>a.value=typeof i=="string"?i:"";return()=>n("div",{},n(t,{...e,modelValue:a.value,"onUpdate:modelValue":p},{default:()=>a.value}))}}),name:"v-model"},s={...u,name:"With placeholder",args:{placeholder:"Enter something here"}},l={...u,name:"With label text",args:{labelText:"Label:"}},d={render:e=>({components:{VInputField:t},setup(){return()=>n("div",{},[n("label",{for:"field"},"Label:"),n(t,{...e})])}}),name:"With custom label"},c={...u,name:"With connections",args:{connectionSides:["start","end"]}};var m,h,f;r.parameters={...r.parameters,docs:{...(m=r.parameters)==null?void 0:m.docs,source:{originalSource:`{
  ...Template,
  name: "Default",
  args: {
    value: "Text goes here"
  }
}`,...(f=(h=r.parameters)==null?void 0:h.docs)==null?void 0:f.source}}};var g,b,x;o.parameters={...o.parameters,docs:{...(g=o.parameters)==null?void 0:g.docs,source:{originalSource:`{
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
}`,...(x=(b=o.parameters)==null?void 0:b.docs)==null?void 0:x.source}}};var W,v,T;s.parameters={...s.parameters,docs:{...(W=s.parameters)==null?void 0:W.docs,source:{originalSource:`{
  ...Template,
  name: "With placeholder",
  args: {
    placeholder: "Enter something here"
  }
}`,...(T=(v=s.parameters)==null?void 0:v.docs)==null?void 0:T.source}}};var V,y,I;l.parameters={...l.parameters,docs:{...(V=l.parameters)==null?void 0:V.docs,source:{originalSource:`{
  ...Template,
  name: "With label text",
  args: {
    labelText: "Label:"
  }
}`,...(I=(y=l.parameters)==null?void 0:y.docs)==null?void 0:I.source}}};var D,L,w;d.parameters={...d.parameters,docs:{...(D=d.parameters)==null?void 0:D.docs,source:{originalSource:`{
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
}`,...(w=(L=d.parameters)==null?void 0:L.docs)==null?void 0:w.source}}};var S,F,_;c.parameters={...c.parameters,docs:{...(S=c.parameters)==null?void 0:S.docs,source:{originalSource:`{
  ...Template,
  name: "With connections",
  args: {
    connectionSides: ["start", "end"]
  }
}`,...(_=(F=c.parameters)==null?void 0:F.docs)==null?void 0:_.source}}};const O=["Default","VModel","WithPlaceholder","WithLabelText","WithCustomLabel","WithConnections"];export{r as Default,o as VModel,c as WithConnections,d as WithCustomLabel,l as WithLabelText,s as WithPlaceholder,O as __namedExportsOrder,P as default};
