(function(){try{var e=typeof window<"u"?window:typeof o<"u"?o:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="31d31892-2cc3-4d22-9dac-fa1196bcdccc",e._sentryDebugIdIdentifier="sentry-dbid-31d31892-2cc3-4d22-9dac-fa1196bcdccc")}catch{}})();const{STORY_CHANGED:a}=__STORYBOOK_MODULE_CORE_EVENTS__,{addons:h}=__STORYBOOK_MODULE_PREVIEW_API__,{global:o}=__STORYBOOK_MODULE_GLOBAL__;var s="storybook/highlight",l="storybookHighlight",g=`${s}/add`,y=`${s}/reset`,{document:_}=o,I=(e="#FF4785",t="dashed")=>`
  outline: 2px ${t} ${e};
  outline-offset: 2px;
  box-shadow: 0 0 0 6px rgba(255,255,255,0.6);
`,i=h.getChannel(),O=e=>{let t=l;r();let d=Array.from(new Set(e.elements)),n=_.createElement("style");n.setAttribute("id",t),n.innerHTML=d.map(c=>`${c}{
          ${I(e.color,e.style)}
         }`).join(" "),_.head.appendChild(n)},r=()=>{var d;let e=l,t=_.getElementById(e);t&&((d=t.parentNode)==null||d.removeChild(t))};i.on(a,r);i.on(y,r);i.on(g,O);
