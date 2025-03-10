import{h as r}from"./53SD24Bo.js";import{_ as t}from"./bkmVosP6.js";import"./RQxsyxdU.js";import"./CRVDSoCQ.js";import"./f6gYKWT5.js";import"./D6RfD4r0.js";import"./BbcJJQG6.js";import"./BW6nfHgy.js";import"./BjsSTAr7.js";import"./Cai0IfA4.js";import"./7RO02bE1.js";import"./CGjrUY8T.js";import"./DXnxRZFx.js";import"./B2IxrC02.js";import"./CLVl6rL5.js";import"./C-ucudUc.js";import"./BALwooav.js";import"./CxEt8vcx.js";import"./BnJv8bNI.js";import"./okj3qyDJ.js";import"./BUSEWVk8.js";import"./ByZ6H8Q9.js";import"./oAL5f6fw.js";import"./B7ZxQ_gM.js";import"./CGdESDy3.js";import"./C4QhmNcb.js";import"./CxzE6WfI.js";import"./BsOxdBIg.js";import"./DhTbjJlp.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},n=new e.Error().stack;n&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[n]="634c5bb3-2d98-4cf4-860b-662acb9ed66d",e._sentryDebugIdIdentifier="sentry-dbid-634c5bb3-2d98-4cf4-860b-662acb9ed66d")}catch{}})();const w={mediaType:{options:["audio","image"],control:{type:"radio"}},isSelected:{control:{type:"boolean"}},layout:{options:["stacked","horizontal"],control:{type:"radio"}}},U={title:"Components/VContentLink",component:t,argTypes:w},a={render:e=>({components:{VContentLink:t},setup(){return()=>r(t,e)}}),name:"Default",args:{mediaType:"image",labels:{aria:"View 5708 image results for cat",visible:"View 5708 image"},to:"/search/image/?q=cat"}},i={name:"Horizontal",render:e=>({components:{VContentLink:t},setup(){const n={image:5708,audio:4561}[e.mediaType],o={aria:`View ${n} ${e.mediaType} results for cat`,visible:`View ${n} ${e.mediaType}`};return()=>r("div",{class:"max-w-md"},[r(t,{...e,labels:o})])}}),args:{mediaType:"audio",layout:"horizontal"}},s={render:()=>({components:{VContentLink:t},setup(){const e=[{mediaType:"image",resultsCount:4321},{mediaType:"audio",resultsCount:1234}];return()=>r("div",{class:"max-w-md mb-4 mt-2 grid grid-cols-2 gap-4 md:mt-0"},e.map(({mediaType:n,resultsCount:o},f)=>r(t,{mediaType:n,labels:{aria:`View ${o} ${n} results for cat`,visible:`View ${o} ${n}`},to:`/search/${n}/?q=cat`,key:f})))}}),name:"Mobile",parameters:{viewport:{defaultViewport:"xs"}}};var m,p,d;a.parameters={...a.parameters,docs:{...(m=a.parameters)==null?void 0:m.docs,source:{originalSource:`{
  render: args => ({
    components: {
      VContentLink
    },
    setup() {
      return () => h(VContentLink, args);
    }
  }),
  name: "Default",
  args: {
    mediaType: "image",
    labels: {
      aria: \`View 5708 image results for cat\`,
      visible: \`View 5708 image\`
    },
    to: "/search/image/?q=cat"
  }
}`,...(d=(p=a.parameters)==null?void 0:p.docs)==null?void 0:d.source}}};var c,l,u;i.parameters={...i.parameters,docs:{...(c=i.parameters)==null?void 0:c.docs,source:{originalSource:`{
  name: "Horizontal",
  render: args => ({
    components: {
      VContentLink
    },
    setup() {
      const count = {
        image: 5708,
        audio: 4561
      }[args.mediaType];
      const labels = {
        aria: \`View \${count} \${args.mediaType} results for cat\`,
        visible: \`View \${count} \${args.mediaType}\`
      };
      return () => h("div", {
        class: "max-w-md"
      }, [h(VContentLink, {
        ...args,
        labels
      })]);
    }
  }),
  args: {
    mediaType: "audio",
    layout: "horizontal"
  } as typeof VContentLink.props
}`,...(u=(l=i.parameters)==null?void 0:l.docs)==null?void 0:u.source}}};var y,g,b;s.parameters={...s.parameters,docs:{...(y=s.parameters)==null?void 0:y.docs,source:{originalSource:`{
  render: () => ({
    components: {
      VContentLink
    },
    setup() {
      const types = [{
        mediaType: "image",
        resultsCount: 4321
      }, {
        mediaType: "audio",
        resultsCount: 1234
      }];
      return () => h("div", {
        class: "max-w-md mb-4 mt-2 grid grid-cols-2 gap-4 md:mt-0"
      }, types.map(({
        mediaType,
        resultsCount
      }, key) => h(VContentLink, {
        mediaType: mediaType as SupportedMediaType,
        labels: {
          aria: \`View \${resultsCount} \${mediaType} results for cat\`,
          visible: \`View \${resultsCount} \${mediaType}\`
        },
        to: \`/search/\${mediaType}/?q=cat\`,
        key
      })));
    }
  }),
  name: "Mobile",
  parameters: {
    viewport: {
      defaultViewport: "xs"
    }
  }
}`,...(b=(g=s.parameters)==null?void 0:g.docs)==null?void 0:b.source}}};const W=["Default","Horizontal","Mobile"];export{a as Default,i as Horizontal,s as Mobile,W as __namedExportsOrder,U as default};
