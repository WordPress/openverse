import{u as m}from"./Bmz-fAWG.js";import{u as c}from"./gmSLTnsl.js";import{V as e}from"./CgYdn_jN.js";import{h as r}from"./D21kBugn.js";import"./KtaE-n0E.js";import"./CRWjC3CT.js";import"./CTON8dBl.js";import"./Dt-H8hG_.js";import"./DmWT6tLV.js";import"./C66CHCZN.js";import"./Ci7G4jyV.js";import"./Cpj98o6Y.js";import"./Xs_VBmP5.js";import"./BQsRc94L.js";import"./JYtQN4fY.js";import"./CszWEYKx.js";import"./CVtkxrq9.js";import"./D0ww02ZN.js";import"./C_KzvzgK.js";import"./K-1Rbgrz.js";import"./CFMQYC2y.js";import"./DzUJZ0J9.js";import"./DEweiwTv.js";import"./DlAUqK2U.js";import"./CHtSUrKH.js";import"./DL71xeF0.js";import"./CWkdu0ct.js";import"./BOX21o1p.js";import"./CwFRh6_2.js";import"./BMFse2nb.js";import"./Cs0FBLOW.js";import"./DyBDyB1K.js";import"./C1YDwe8s.js";const s=[{source_name:"smithsonian_african_american_history_museum",display_name:"Smithsonian Institution: National Museum of African American History and Culture",source_url:"https://nmaahc.si.edu",logo_url:null,media_count:10895},{source_name:"flickr",display_name:"Flickr",source_url:"https://www.flickr.com",logo_url:null,media_count:505849755},{source_name:"met",display_name:"Metropolitan Museum of Art",source_url:"https://www.metmuseum.org",logo_url:null,media_count:396650}],l=["smithsonian_african_american_history_museum","flickr","met"],L={title:"Components/VCollectionHeader",component:e},p=[{collectionName:"tag",collectionParams:{collection:"tag",tag:"cat"},mediaType:"image"},{collectionName:"source",collectionParams:{collection:"source",source:"met"},mediaType:"image"},{collectionName:"creator",collectionParams:{collection:"creator",source:"flickr",creator:"iocyoungreporters"},mediaType:"image",creatorUrl:"https://www.flickr.com/photos/126018610@N05"},{collectionName:"source-with-long-name",collectionParams:{collection:"source",source:"smithsonian_african_american_history_museum"},mediaType:"image"}],o={render:()=>({components:{VCollectionHeader:e},setup(){return c().$patch({providers:{image:s},sourceNames:{image:l}}),m().$patch({results:{image:{count:240}}}),()=>r("div",{class:"wrapper w-full p-3 flex flex-col gap-4 bg-surface"},p.map(n=>r(e,{...n,class:"bg-default"})))}}),name:"All collections"};var t,i,a;o.parameters={...o.parameters,docs:{...(t=o.parameters)==null?void 0:t.docs,source:{originalSource:`{
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
}`,...(a=(i=o.parameters)==null?void 0:i.docs)==null?void 0:a.source}}};const Q=["AllCollections"];export{o as AllCollections,Q as __namedExportsOrder,L as default};
