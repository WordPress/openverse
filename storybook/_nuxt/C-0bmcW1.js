import{h as n}from"./53SD24Bo.js";import{u as m}from"./BziOhplB.js";import{u as l}from"./CNOfB5vH.js";import{V as t}from"./rYJ1Jc7_.js";import"./DSrDAhJH.js";import"./e2yY43HP.js";import"./D9Az8HPp.js";import"./6H5bLa5F.js";import"./CFX3QTN5.js";import"./h1cGCrsl.js";import"./7RO02bE1.js";import"./DDOdTjm7.js";import"./CHnObwfQ.js";import"./iy3krge0.js";import"./DJcnDpKq.js";import"./BWKbF-QS.js";import"./9xj2VA-m.js";import"./okj3qyDJ.js";import"./Cz1YM6_r.js";import"./DW11D-YO.js";import"./ProZPLPW.js";import"./Dkz41V7r.js";import"./Cpe-Oxin.js";import"./CGiaWBvD.js";import"./DhTbjJlp.js";import"./epSsoWbu.js";import"./CHIw9XCH.js";import"./DaaoxyFL.js";import"./B65OKO0j.js";import"./BsDDwWKZ.js";import"./Bzg618fq.js";import"./B9Cuo1Ro.js";import"./BQrorSEU.js";import"./B06vE1PI.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="f8f8df25-0058-4be6-a4bc-8635fa6dacbb",e._sentryDebugIdIdentifier="sentry-dbid-f8f8df25-0058-4be6-a4bc-8635fa6dacbb")}catch{}})();const u=[{source_name:"smithsonian_african_american_history_museum",display_name:"Smithsonian Institution: National Museum of African American History and Culture",source_url:"https://nmaahc.si.edu",logo_url:null,media_count:10895},{source_name:"flickr",display_name:"Flickr",source_url:"https://www.flickr.com",logo_url:null,media_count:505849755},{source_name:"met",display_name:"Metropolitan Museum of Art",source_url:"https://www.metmuseum.org",logo_url:null,media_count:396650}],p=["smithsonian_african_american_history_museum","flickr","met"],R={title:"Components/VCollectionHeader",component:t},d=[{collectionName:"tag",collectionParams:{collection:"tag",tag:"cat"},mediaType:"image"},{collectionName:"source",collectionParams:{collection:"source",source:"met"},mediaType:"image"},{collectionName:"creator",collectionParams:{collection:"creator",source:"flickr",creator:"iocyoungreporters"},mediaType:"image",creatorUrl:"https://www.flickr.com/photos/126018610@N05"},{collectionName:"source-with-long-name",collectionParams:{collection:"source",source:"smithsonian_african_american_history_museum"},mediaType:"image"}],o={render:()=>({components:{VCollectionHeader:t},setup(){return l().$patch({providers:{image:u},sourceNames:{image:p}}),m().$patch({results:{image:{count:240}},mediaFetchState:{image:{status:"success",error:null},audio:{status:"success",error:null}}}),()=>n("div",{class:"wrapper w-full p-3 flex flex-col gap-4 bg-surface"},d.map(i=>n(t,{...i,class:"bg-default"})))}}),name:"All collections"};var a,s,c;o.parameters={...o.parameters,docs:{...(a=o.parameters)==null?void 0:a.docs,source:{originalSource:`{
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
