import{h as n}from"./53SD24Bo.js";import{u as m}from"./Cu8oCyfM.js";import{u as l}from"./CnJShkNX.js";import{V as t}from"./Z4dO6lSq.js";import"./DxXQfK2h.js";import"./DEUQKZ_9.js";import"./CGl8BGyI.js";import"./Bl44UfZi.js";import"./CrtbdNAL.js";import"./BfmvDfJj.js";import"./7RO02bE1.js";import"./7T7Oyunt.js";import"./aM5GB1sa.js";import"./JKyArXdZ.js";import"./CJn6N6md.js";import"./GK6z1vC-.js";import"./DCBI9Hp4.js";import"./okj3qyDJ.js";import"./Ca-grqql.js";import"./COHSvtot.js";import"./CbQ_U0bA.js";import"./1q_AdtTO.js";import"./CO_nLv6a.js";import"./DY7Jae7t.js";import"./DhTbjJlp.js";import"./fqELieEp.js";import"./D0PbCr5t.js";import"./Do357AjE.js";import"./Ab-gfhxw.js";import"./y5FwBbW3.js";import"./m1m5Z0c3.js";import"./B9Cuo1Ro.js";import"./BQrorSEU.js";import"./B06vE1PI.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="f8f8df25-0058-4be6-a4bc-8635fa6dacbb",e._sentryDebugIdIdentifier="sentry-dbid-f8f8df25-0058-4be6-a4bc-8635fa6dacbb")}catch{}})();const u=[{source_name:"smithsonian_african_american_history_museum",display_name:"Smithsonian Institution: National Museum of African American History and Culture",source_url:"https://nmaahc.si.edu",logo_url:null,media_count:10895},{source_name:"flickr",display_name:"Flickr",source_url:"https://www.flickr.com",logo_url:null,media_count:505849755},{source_name:"met",display_name:"Metropolitan Museum of Art",source_url:"https://www.metmuseum.org",logo_url:null,media_count:396650}],p=["smithsonian_african_american_history_museum","flickr","met"],R={title:"Components/VCollectionHeader",component:t},d=[{collectionName:"tag",collectionParams:{collection:"tag",tag:"cat"},mediaType:"image"},{collectionName:"source",collectionParams:{collection:"source",source:"met"},mediaType:"image"},{collectionName:"creator",collectionParams:{collection:"creator",source:"flickr",creator:"iocyoungreporters"},mediaType:"image",creatorUrl:"https://www.flickr.com/photos/126018610@N05"},{collectionName:"source-with-long-name",collectionParams:{collection:"source",source:"smithsonian_african_american_history_museum"},mediaType:"image"}],o={render:()=>({components:{VCollectionHeader:t},setup(){return l().$patch({providers:{image:u},sourceNames:{image:p}}),m().$patch({results:{image:{count:240}},mediaFetchState:{image:{status:"success",error:null},audio:{status:"success",error:null}}}),()=>n("div",{class:"wrapper w-full p-3 flex flex-col gap-4 bg-surface"},d.map(i=>n(t,{...i,class:"bg-default"})))}}),name:"All collections"};var a,s,c;o.parameters={...o.parameters,docs:{...(a=o.parameters)==null?void 0:a.docs,source:{originalSource:`{
  render: () => ({
    components: {
      VCollectionHeader
    },
    setup() {
      const providerStore = useProviderStore();
      providerStore.$patch({
        providers: {
          image: imageProviders
        },
        sourceNames: {
          image: imageProviderNames
        }
      });
      const mediaStore = useMediaStore();
      mediaStore.$patch({
        results: {
          image: {
            count: 240
          }
        },
        mediaFetchState: {
          image: {
            status: "success",
            error: null
          },
          audio: {
            status: "success",
            error: null
          }
        }
      });
      return () => h("div", {
        class: "wrapper w-full p-3 flex flex-col gap-4 bg-surface"
      }, collections.map(collection => h(VCollectionHeader, {
        ...(collection as typeof VCollectionHeader.props),
        class: "bg-default"
      })));
    }
  }),
  name: "All collections"
}`,...(c=(s=o.parameters)==null?void 0:s.docs)==null?void 0:c.source}}};const W=["AllCollections"];export{o as AllCollections,W as __namedExportsOrder,R as default};
