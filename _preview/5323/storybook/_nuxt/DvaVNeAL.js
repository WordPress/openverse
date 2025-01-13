import{h as n}from"./DwwldUEF.js";import{u as m}from"./BNZBDzqs.js";import{u as l}from"./BZyg411k.js";import{V as t}from"./BHrbNqFF.js";import"./_APRZIM1.js";import"./CVIvqSzo.js";import"./B6xXmqkp.js";import"./hEU2uDsT.js";import"./DbbxtPJM.js";import"./BAbDw2j1.js";import"./Ck0CgHQL.js";import"./Chgn5vcY.js";import"./DfKQSGJ_.js";import"./HE8VvABB.js";import"./BcTEa7d-.js";import"./D2_E7_fN.js";import"./zgpsPOGm.js";import"./DzAq6MI-.js";import"./--8yokH5.js";import"./5Ry8iPjm.js";import"./Dy2lpsBJ.js";import"./Dv6gP7wZ.js";import"./erT4Ktbo.js";import"./zDkj65pD.js";import"./DhTbjJlp.js";import"./B1esKRaU.js";import"./BRLy_Msv.js";import"./D197vL4o.js";import"./DS5pDSwp.js";import"./srXH8gEg.js";import"./BS9mcOP4.js";import"./D93TPuWH.js";import"./CU-snwr6.js";import"./DNI0JtzU.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="f8f8df25-0058-4be6-a4bc-8635fa6dacbb",e._sentryDebugIdIdentifier="sentry-dbid-f8f8df25-0058-4be6-a4bc-8635fa6dacbb")}catch{}})();const u=[{source_name:"smithsonian_african_american_history_museum",display_name:"Smithsonian Institution: National Museum of African American History and Culture",source_url:"https://nmaahc.si.edu",logo_url:null,media_count:10895},{source_name:"flickr",display_name:"Flickr",source_url:"https://www.flickr.com",logo_url:null,media_count:505849755},{source_name:"met",display_name:"Metropolitan Museum of Art",source_url:"https://www.metmuseum.org",logo_url:null,media_count:396650}],p=["smithsonian_african_american_history_museum","flickr","met"],R={title:"Components/VCollectionHeader",component:t},d=[{collectionName:"tag",collectionParams:{collection:"tag",tag:"cat"},mediaType:"image"},{collectionName:"source",collectionParams:{collection:"source",source:"met"},mediaType:"image"},{collectionName:"creator",collectionParams:{collection:"creator",source:"flickr",creator:"iocyoungreporters"},mediaType:"image",creatorUrl:"https://www.flickr.com/photos/126018610@N05"},{collectionName:"source-with-long-name",collectionParams:{collection:"source",source:"smithsonian_african_american_history_museum"},mediaType:"image"}],o={render:()=>({components:{VCollectionHeader:t},setup(){return l().$patch({providers:{image:u},sourceNames:{image:p}}),m().$patch({results:{image:{count:240}},mediaFetchState:{image:{status:"success",error:null},audio:{status:"success",error:null}}}),()=>n("div",{class:"wrapper w-full p-3 flex flex-col gap-4 bg-surface"},d.map(i=>n(t,{...i,class:"bg-default"})))}}),name:"All collections"};var a,s,c;o.parameters={...o.parameters,docs:{...(a=o.parameters)==null?void 0:a.docs,source:{originalSource:`{
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
