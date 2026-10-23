import{h as n}from"./DmrXErv4.js";import{u as m}from"./Boj1x2qa.js";import{u as l}from"./CdQaOBNt.js";import{V as t}from"./CT5rf9Uj.js";import"./Cre_5D1H.js";import"./P7ZX4TMp.js";import"./BWJ9rAf_.js";import"./D8RLh9Dr.js";import"./DFZUF_34.js";import"./B3KNKrKa.js";import"./BxtqxG2r.js";import"./D7WD_DXd.js";import"./D_KYnWat.js";import"./wMBvb-CP.js";import"./CEG4L8Wc.js";import"./B_dsH32H.js";import"./CT8Zrxvs.js";import"./DzAq6MI-.js";import"./C7sHCGoX.js";import"./DWRfakdt.js";import"./CCN4kZnP.js";import"./Bn7RUpRV.js";import"./OMXwMIS8.js";import"./rMKLwKwR.js";import"./Dv0Nl23j.js";import"./DhTbjJlp.js";import"./CC94LAKs.js";import"./qMQTJaHN.js";import"./BRHrr7ck.js";import"./Bpr67t9y.js";import"./ZTn2TBUv.js";import"./zcyFsLMi.js";import"./D5Za6x0E.js";import"./Dx-3nI8A.js";import"./CJ7FTku9.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="ff4bd734-a7ff-48ed-b29b-d77e109481ea",e._sentryDebugIdIdentifier="sentry-dbid-ff4bd734-a7ff-48ed-b29b-d77e109481ea")}catch{}})();const u=[{source_name:"smithsonian_african_american_history_museum",display_name:"Smithsonian Institution: National Museum of African American History and Culture",source_url:"https://nmaahc.si.edu",logo_url:null,media_count:10895},{source_name:"flickr",display_name:"Flickr",source_url:"https://www.flickr.com",logo_url:null,media_count:505849755},{source_name:"met",display_name:"Metropolitan Museum of Art",source_url:"https://www.metmuseum.org",logo_url:null,media_count:396650}],p=["smithsonian_african_american_history_museum","flickr","met"],W={title:"Components/VCollectionHeader",component:t},d=[{collectionName:"tag",collectionParams:{collection:"tag",tag:"cat"},mediaType:"image"},{collectionName:"source",collectionParams:{collection:"source",source:"met"},mediaType:"image"},{collectionName:"creator",collectionParams:{collection:"creator",source:"flickr",creator:"iocyoungreporters"},mediaType:"image",creatorUrl:"https://www.flickr.com/photos/126018610@N05"},{collectionName:"source-with-long-name",collectionParams:{collection:"source",source:"smithsonian_african_american_history_museum"},mediaType:"image"}],o={render:()=>({components:{VCollectionHeader:t},setup(){return l().$patch({providers:{image:u},sourceNames:{image:p}}),m().$patch({results:{image:{count:240}},mediaFetchState:{image:{status:"success",error:null},audio:{status:"success",error:null}}}),()=>n("div",{class:"wrapper w-full p-3 flex flex-col gap-4 bg-surface"},d.map(i=>n(t,{...i,class:"bg-default"})))}}),name:"All collections"};var a,s,c;o.parameters={...o.parameters,docs:{...(a=o.parameters)==null?void 0:a.docs,source:{originalSource:`{
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
}`,...(c=(s=o.parameters)==null?void 0:s.docs)==null?void 0:c.source}}};const X=["AllCollections"];export{o as AllCollections,X as __namedExportsOrder,W as default};
