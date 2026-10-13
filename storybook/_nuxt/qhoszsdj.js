import{h as n}from"./DmrXErv4.js";import{u as m}from"./-2B6Z20n.js";import{u as l}from"./Dyqkukzd.js";import{V as t}from"./DRSW16W7.js";import"./Ceavzuo-.js";import"./Dbo3V4Mp.js";import"./9mLNX8sN.js";import"./DNv5NVgs.js";import"./i2yG8VlY.js";import"./Dp2jPxn_.js";import"./BxtqxG2r.js";import"./Bp0tQXh7.js";import"./COQlapGP.js";import"./JU2JEH3o.js";import"./FWiT1Y5Q.js";import"./BS_ZT77X.js";import"./C_FySRQg.js";import"./DzAq6MI-.js";import"./DoeNFUMW.js";import"./CtkidDXQ.js";import"./CMZS2cOm.js";import"./BayljJpb.js";import"./Ck0gvfbg.js";import"./CdX5GYQk.js";import"./qy-jYTsH.js";import"./DhTbjJlp.js";import"./CCWBXjfD.js";import"./Bf1ZO8EJ.js";import"./0xbGHjBU.js";import"./lCCmDL6e.js";import"./CtS8164B.js";import"./us_YXsMU.js";import"./D5Za6x0E.js";import"./Dx-3nI8A.js";import"./CJ7FTku9.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="ff4bd734-a7ff-48ed-b29b-d77e109481ea",e._sentryDebugIdIdentifier="sentry-dbid-ff4bd734-a7ff-48ed-b29b-d77e109481ea")}catch{}})();const u=[{source_name:"smithsonian_african_american_history_museum",display_name:"Smithsonian Institution: National Museum of African American History and Culture",source_url:"https://nmaahc.si.edu",logo_url:null,media_count:10895},{source_name:"flickr",display_name:"Flickr",source_url:"https://www.flickr.com",logo_url:null,media_count:505849755},{source_name:"met",display_name:"Metropolitan Museum of Art",source_url:"https://www.metmuseum.org",logo_url:null,media_count:396650}],p=["smithsonian_african_american_history_museum","flickr","met"],W={title:"Components/VCollectionHeader",component:t},d=[{collectionName:"tag",collectionParams:{collection:"tag",tag:"cat"},mediaType:"image"},{collectionName:"source",collectionParams:{collection:"source",source:"met"},mediaType:"image"},{collectionName:"creator",collectionParams:{collection:"creator",source:"flickr",creator:"iocyoungreporters"},mediaType:"image",creatorUrl:"https://www.flickr.com/photos/126018610@N05"},{collectionName:"source-with-long-name",collectionParams:{collection:"source",source:"smithsonian_african_american_history_museum"},mediaType:"image"}],o={render:()=>({components:{VCollectionHeader:t},setup(){return l().$patch({providers:{image:u},sourceNames:{image:p}}),m().$patch({results:{image:{count:240}},mediaFetchState:{image:{status:"success",error:null},audio:{status:"success",error:null}}}),()=>n("div",{class:"wrapper w-full p-3 flex flex-col gap-4 bg-surface"},d.map(i=>n(t,{...i,class:"bg-default"})))}}),name:"All collections"};var a,s,c;o.parameters={...o.parameters,docs:{...(a=o.parameters)==null?void 0:a.docs,source:{originalSource:`{
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
