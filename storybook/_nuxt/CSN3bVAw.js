import{h as n}from"./53SD24Bo.js";import{u as m}from"./D6RfD4r0.js";import{u as l}from"./CLVl6rL5.js";import{V as t}from"./CWS-TSE3.js";import"./RQxsyxdU.js";import"./BbcJJQG6.js";import"./f6gYKWT5.js";import"./BW6nfHgy.js";import"./BjsSTAr7.js";import"./Cai0IfA4.js";import"./7RO02bE1.js";import"./CGjrUY8T.js";import"./DXnxRZFx.js";import"./B2IxrC02.js";import"./CxEt8vcx.js";import"./BALwooav.js";import"./BnJv8bNI.js";import"./okj3qyDJ.js";import"./C-ucudUc.js";import"./B7ZxQ_gM.js";import"./CGdESDy3.js";import"./C4QhmNcb.js";import"./CxzE6WfI.js";import"./BsOxdBIg.js";import"./DhTbjJlp.js";import"./DiDEpn9B.js";import"./I7NgnUkk.js";import"./ByZ6H8Q9.js";import"./oAL5f6fw.js";import"./C2aFgytJ.js";import"./B6C3U6x3.js";import"./DLCnOpdB.js";import"./BQrorSEU.js";import"./B06vE1PI.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="f8f8df25-0058-4be6-a4bc-8635fa6dacbb",e._sentryDebugIdIdentifier="sentry-dbid-f8f8df25-0058-4be6-a4bc-8635fa6dacbb")}catch{}})();const u=[{source_name:"smithsonian_african_american_history_museum",display_name:"Smithsonian Institution: National Museum of African American History and Culture",source_url:"https://nmaahc.si.edu",logo_url:null,media_count:10895},{source_name:"flickr",display_name:"Flickr",source_url:"https://www.flickr.com",logo_url:null,media_count:505849755},{source_name:"met",display_name:"Metropolitan Museum of Art",source_url:"https://www.metmuseum.org",logo_url:null,media_count:396650}],p=["smithsonian_african_american_history_museum","flickr","met"],R={title:"Components/VCollectionHeader",component:t},d=[{collectionName:"tag",collectionParams:{collection:"tag",tag:"cat"},mediaType:"image"},{collectionName:"source",collectionParams:{collection:"source",source:"met"},mediaType:"image"},{collectionName:"creator",collectionParams:{collection:"creator",source:"flickr",creator:"iocyoungreporters"},mediaType:"image",creatorUrl:"https://www.flickr.com/photos/126018610@N05"},{collectionName:"source-with-long-name",collectionParams:{collection:"source",source:"smithsonian_african_american_history_museum"},mediaType:"image"}],o={render:()=>({components:{VCollectionHeader:t},setup(){return l().$patch({providers:{image:u},sourceNames:{image:p}}),m().$patch({results:{image:{count:240}},mediaFetchState:{image:{status:"success",error:null},audio:{status:"success",error:null}}}),()=>n("div",{class:"wrapper w-full p-3 flex flex-col gap-4 bg-surface"},d.map(i=>n(t,{...i,class:"bg-default"})))}}),name:"All collections"};var a,s,c;o.parameters={...o.parameters,docs:{...(a=o.parameters)==null?void 0:a.docs,source:{originalSource:`{
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
