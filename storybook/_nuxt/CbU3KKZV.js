import{d as H}from"./DM0lS_Sl.js";(function(){try{var r=typeof E<"u"?E:typeof I<"u"?I:typeof self<"u"?self:{},e=new r.Error().stack;e&&(r._sentryDebugIds=r._sentryDebugIds||{},r._sentryDebugIds[e]="a5134870-7d2c-4c40-8010-b9a22727ee56",r._sentryDebugIdIdentifier="sentry-dbid-a5134870-7d2c-4c40-8010-b9a22727ee56")}catch{}})();const{useEffect:A,useMemo:h}=__STORYBOOK_MODULE_PREVIEW_API__,{global:I}=__STORYBOOK_MODULE_GLOBAL__,{logger:K}=__STORYBOOK_MODULE_CLIENT_LOGGER__;var p="backgrounds",C={light:{name:"light",value:"#F8F8F8"},dark:{name:"dark",value:"#333"}},{document:b,window:E}=I,D=()=>{var r;return!!((r=E==null?void 0:E.matchMedia("(prefers-reduced-motion: reduce)"))!=null&&r.matches)},B=r=>{(Array.isArray(r)?r:[r]).forEach(P)},P=r=>{var d;let e=b.getElementById(r);e&&((d=e.parentElement)==null||d.removeChild(e))},z=(r,e)=>{let d=b.getElementById(r);if(d)d.innerHTML!==e&&(d.innerHTML=e);else{let n=b.createElement("style");n.setAttribute("id",r),n.innerHTML=e,b.head.appendChild(n)}},U=(r,e,d)=>{var a;let n=b.getElementById(r);if(n)n.innerHTML!==e&&(n.innerHTML=e);else{let t=b.createElement("style");t.setAttribute("id",r),t.innerHTML=e;let i=`addon-backgrounds-grid${d?`-docs-${d}`:""}`,o=b.getElementById(i);o?(a=o.parentElement)==null||a.insertBefore(t,o):b.head.appendChild(t)}},j={cellSize:100,cellAmount:10,opacity:.8},G="addon-backgrounds",R="addon-backgrounds-grid",X=D()?"":"transition: background-color 0.3s;",N=(r,e)=>{let{globals:d,parameters:n,viewMode:a,id:t}=e,{options:i=C,disable:o,grid:s=j}=n[p]||{},u=d[p]||{},c=u.value,l=c?i[c]:void 0,$=(l==null?void 0:l.value)||"transparent",m=u.grid||!1,y=!!l&&!o,f=a==="docs"?`#anchor--${t} .docs-story`:".sb-show-main",_=a==="docs"?`#anchor--${t} .docs-story`:".sb-show-main",F=n.layout===void 0||n.layout==="padded",L=a==="docs"?20:F?16:0,{cellAmount:k,cellSize:g,opacity:x,offsetX:S=L,offsetY:v=L}=s,M=a==="docs"?`${G}-docs-${t}`:`${G}-color`,w=a==="docs"?t:null;A(()=>{let T=`
    ${f} {
      background: ${$} !important;
      ${X}
      }`;if(!y){B(M);return}U(M,T,w)},[f,M,w,y,$]);let O=a==="docs"?`${R}-docs-${t}`:`${R}`;return A(()=>{if(!m){B(O);return}let T=[`${g*k}px ${g*k}px`,`${g*k}px ${g*k}px`,`${g}px ${g}px`,`${g}px ${g}px`].join(", "),Y=`
        ${_} {
          background-size: ${T} !important;
          background-position: ${S}px ${v}px, ${S}px ${v}px, ${S}px ${v}px, ${S}px ${v}px !important;
          background-blend-mode: difference !important;
          background-image: linear-gradient(rgba(130, 130, 130, ${x}) 1px, transparent 1px),
           linear-gradient(90deg, rgba(130, 130, 130, ${x}) 1px, transparent 1px),
           linear-gradient(rgba(130, 130, 130, ${x/2}) 1px, transparent 1px),
           linear-gradient(90deg, rgba(130, 130, 130, ${x/2}) 1px, transparent 1px) !important;
        }
      `;z(O,Y)},[k,g,_,O,m,S,v,x]),r()},W=(r,e=[],d)=>{if(r==="transparent")return"transparent";if(e.find(a=>a.value===r)||r)return r;let n=e.find(a=>a.name===d);if(n)return n.value;if(d){let a=e.map(t=>t.name).join(", ");K.warn(H`
        Backgrounds Addon: could not find the default color "${d}".
        These are the available colors for your story based on your configuration:
        ${a}.
      `)}return"transparent"},q=(r,e)=>{var c;let{globals:d,parameters:n}=e,a=(c=d[p])==null?void 0:c.value,t=n[p],i=h(()=>t.disable?"transparent":W(a,t.values,t.default),[t,a]),o=h(()=>i&&i!=="transparent",[i]),s=e.viewMode==="docs"?`#anchor--${e.id} .docs-story`:".sb-show-main",u=h(()=>`
      ${s} {
        background: ${i} !important;
        ${D()?"":"transition: background-color 0.3s;"}
      }
    `,[i,s]);return A(()=>{let l=e.viewMode==="docs"?`addon-backgrounds-docs-${e.id}`:"addon-backgrounds-color";if(!o){B(l);return}U(l,u,e.viewMode==="docs"?e.id:null)},[o,u,e]),r()},J=(r,e)=>{var y;let{globals:d,parameters:n}=e,a=n[p].grid,t=((y=d[p])==null?void 0:y.grid)===!0&&a.disable!==!0,{cellAmount:i,cellSize:o,opacity:s}=a,u=e.viewMode==="docs",c=n.layout===void 0||n.layout==="padded"?16:0,l=a.offsetX??(u?20:c),$=a.offsetY??(u?20:c),m=h(()=>{let f=e.viewMode==="docs"?`#anchor--${e.id} .docs-story`:".sb-show-main",_=[`${o*i}px ${o*i}px`,`${o*i}px ${o*i}px`,`${o}px ${o}px`,`${o}px ${o}px`].join(", ");return`
      ${f} {
        background-size: ${_} !important;
        background-position: ${l}px ${$}px, ${l}px ${$}px, ${l}px ${$}px, ${l}px ${$}px !important;
        background-blend-mode: difference !important;
        background-image: linear-gradient(rgba(130, 130, 130, ${s}) 1px, transparent 1px),
         linear-gradient(90deg, rgba(130, 130, 130, ${s}) 1px, transparent 1px),
         linear-gradient(rgba(130, 130, 130, ${s/2}) 1px, transparent 1px),
         linear-gradient(90deg, rgba(130, 130, 130, ${s/2}) 1px, transparent 1px) !important;
      }
    `},[o]);return A(()=>{let f=e.viewMode==="docs"?`addon-backgrounds-grid-docs-${e.id}`:"addon-backgrounds-grid";if(!t){B(f);return}z(f,m)},[t,m,e]),r()},V=FEATURES!=null&&FEATURES.backgroundsStoryGlobals?[N]:[J,q],ee={[p]:{grid:{cellSize:20,opacity:.5,cellAmount:5},disable:!1,...!(FEATURES!=null&&FEATURES.backgroundsStoryGlobals)&&{values:Object.values(C)}}},Q={[p]:{value:void 0,grid:!1}},re=FEATURES!=null&&FEATURES.backgroundsStoryGlobals?Q:{[p]:null};export{V as decorators,re as initialGlobals,ee as parameters};
