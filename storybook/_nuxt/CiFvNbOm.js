import{h as n}from"./53SD24Bo.js";import{u as m}from"./CI6-PtcM.js";import{u as l}from"./DZSCtjcm.js";import{V as t}from"./CzjMDkWF.js";import"./Bk8VSEei.js";import"./D4B1y8Wp.js";import"./BSHtV9yS.js";import"./DBpyOWk7.js";import"./Cx3b_-up.js";import"./DLXib-Qm.js";import"./7RO02bE1.js";import"./7RAMVlBS.js";import"./CA_M5S-4.js";import"./whaKyvbR.js";import"./B8akBo1x.js";import"./D1l3oJXo.js";import"./S07_m3Bd.js";import"./okj3qyDJ.js";import"./DUD5NJ41.js";import"./Cbq1TCLb.js";import"./fL1fV1YB.js";import"./C7m8LBdt.js";import"./CQ3yco75.js";import"./b8e1KD_n.js";import"./DhTbjJlp.js";import"./DEtmG7iQ.js";import"./m6oHz-Z8.js";import"./Cpzk_0_B.js";import"./Bl5m8s2n.js";import"./DY6exa3a.js";import"./C0eb6efW.js";import"./B9Cuo1Ro.js";import"./BQrorSEU.js";import"./B06vE1PI.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="f8f8df25-0058-4be6-a4bc-8635fa6dacbb",e._sentryDebugIdIdentifier="sentry-dbid-f8f8df25-0058-4be6-a4bc-8635fa6dacbb")}catch{}})();const u=[{source_name:"smithsonian_african_american_history_museum",display_name:"Smithsonian Institution: National Museum of African American History and Culture",source_url:"https://nmaahc.si.edu",logo_url:null,media_count:10895},{source_name:"flickr",display_name:"Flickr",source_url:"https://www.flickr.com",logo_url:null,media_count:505849755},{source_name:"met",display_name:"Metropolitan Museum of Art",source_url:"https://www.metmuseum.org",logo_url:null,media_count:396650}],p=["smithsonian_african_american_history_museum","flickr","met"],R={title:"Components/VCollectionHeader",component:t},d=[{collectionName:"tag",collectionParams:{collection:"tag",tag:"cat"},mediaType:"image"},{collectionName:"source",collectionParams:{collection:"source",source:"met"},mediaType:"image"},{collectionName:"creator",collectionParams:{collection:"creator",source:"flickr",creator:"iocyoungreporters"},mediaType:"image",creatorUrl:"https://www.flickr.com/photos/126018610@N05"},{collectionName:"source-with-long-name",collectionParams:{collection:"source",source:"smithsonian_african_american_history_museum"},mediaType:"image"}],o={render:()=>({components:{VCollectionHeader:t},setup(){return l().$patch({providers:{image:u},sourceNames:{image:p}}),m().$patch({results:{image:{count:240}},mediaFetchState:{image:{status:"success",error:null},audio:{status:"success",error:null}}}),()=>n("div",{class:"wrapper w-full p-3 flex flex-col gap-4 bg-surface"},d.map(i=>n(t,{...i,class:"bg-default"})))}}),name:"All collections"};var a,s,c;o.parameters={...o.parameters,docs:{...(a=o.parameters)==null?void 0:a.docs,source:{originalSource:`{
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
