import{_ as a}from"./Bv9HkhrL.js";import{_ as p,V as s}from"./D_mCtSu9.js";import{h as e,d}from"./D21kBugn.js";import"./D8Wpa1kZ.js";import"./DzUJZ0J9.js";import"./DEweiwTv.js";import"./CFMQYC2y.js";import"./DlAUqK2U.js";import"./RevM6cLn.js";import"./D4JcsNEP.js";import"./BOX21o1p.js";import"./DmWT6tLV.js";import"./C_KzvzgK.js";import"./K-1Rbgrz.js";import"./JYtQN4fY.js";const l=d({name:"VFilterTabWrapper",props:{appliedFilterCount:{type:Number,required:!0},selectedId:{type:String,required:!0}},setup(r){return()=>e("div",{class:"p-2"},[e(p,{label:"tabs",selectedId:r.selectedId,id:"wrapper",variant:"plain",tablistStyle:"ps-6 pe-2 gap-x-4",class:"flex min-h-0"},{tabs:()=>[e(s,{id:"tab1",label:"Tab 1",size:"medium"},{default:()=>["Tab1"]}),e(a,{appliedFilterCount:r.appliedFilterCount})]}),e("div",{class:"border-t border-default h-2 w-full"})])}}),v={title:"Components/VHeader/VHeaderMobile/VFilterTab",component:l,subcomponents:{VFilterTab:a,VTabs:p,VTab:s},argTypes:{appliedFilterCount:{type:"number"},selectedId:{control:"select",options:["filters","tab1"]}},args:{appliedFilterCount:3,selectedId:"filters"}},t={render:r=>({components:{VFilterTab:a,VTabs:p,VTab:s},setup(){return()=>e(l,{...r},{})}})};var i,o,n;t.parameters={...t.parameters,docs:{...(i=t.parameters)==null?void 0:i.docs,source:{originalSource:`{
  render: args => ({
    components: {
      VFilterTab,
      VTabs,
      VTab
    },
    setup() {
      return () => h(VFilterTabWrapper, {
        ...args
      }, {});
    }
  })
}`,...(n=(o=t.parameters)==null?void 0:o.docs)==null?void 0:n.source}}};const S=["Default"];export{t as Default,S as __namedExportsOrder,v as default};
