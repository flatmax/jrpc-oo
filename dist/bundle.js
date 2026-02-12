/**
 # Copyright (c) 2016-2018 The flatmax-elements Authors. All rights reserved.
 #
 # Redistribution and use in source and binary forms, with or without
 # modification, are permitted provided that the following conditions are
 # met:
 #
 #    * Redistributions of source code must retain the above copyright
 # notice, this list of conditions and the following disclaimer.
 #    * Redistributions in binary form must reproduce the above
 # copyright notice, this list of conditions and the following disclaimer
 # in the documentation and/or other materials provided with the
 # distribution.
 #    * Neither the name of Flatmax Pty Ltd nor the names of its
 # contributors may be used to endorse or promote products derived from
 # this software without specific prior written permission.
 #
 # THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 # "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 # LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 # A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 # OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 # SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 # LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 # DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 # THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 # (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 # OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */


/** Class to expose another class's methods for use with something like js-JRPC
*/
let ExposeClass$1 = class ExposeClass {
  /** Get the functions in a class, without the constructor
  The names include the class name . method name
  \param oName An option name to prepend which doesn't allow inheritance iteration
  \return the functions as an array of strings
  */
  getAllFns(cte, oName) {
    let names=[];
    let p=cte.constructor.prototype;
    // let p=cte.constructor.prototype.__proto__; // swig used to need this to work - leaving here as an example
    // if (p==null) // The old methd required this for non-swig elements, leaving here as a reminder if it bugs out
    //   p=cte.constructor.prototype;
    while (p!=null){ // iterate through the inheritance tree
      let ObjName=p.constructor.name.replace('_exports_',''); // _exports_ is added by swig
      if (oName!=null)
        ObjName=oName;
      if (ObjName !== 'Object'){
        let newNames=Object.getOwnPropertyNames(p).filter(x => ((x !== 'constructor') && x.indexOf('__')<0));
        newNames.forEach((n, i)=>{
          newNames[i]=ObjName+'.'+n;
        });
        names=names.concat(newNames);
      }
      if (oName!=null) // if we have specified the object to parse, then break before iterating through the heirarchy
        break;
      p=p.__proto__;
    }
    return names;
  }

  /** For each function in cte, create a js-JRPC friendly function.
  \param classToExpose Get all functions from this class to expose
  \param name If name is specified, then use it rather then the constructor's name - sometimes necessary when the variable name == class name (e.g. when using SWIG)
  \return An obj with each of cte class's functions extended with js-JRPC required executions (i.e. next)
  */
  exposeAllFns(classToExpose, name){
    let fns=this.getAllFns(classToExpose, name); // get all available functions
    var fnsExp={}; // create a new js-JRPC friendly function for each function
    fns.forEach(function (fnName){
      fnsExp[fnName]=function(params, next){
        Promise.resolve(classToExpose[fnName.substring(fnName.indexOf('.')+1)].apply(classToExpose, params.args))
        .then(function(ret){
          return next(null,ret);
        }).catch(function(err){
          console.log('failed : '+err);
          return next(err);
        });
      };
    });
    //console.log(fnsExp) // uncomment this to see which functions are being exposed.
    return fnsExp;
  }
};

if (typeof module !== 'undefined' && typeof module.exports !== 'undefined')
    module.exports = ExposeClass$1;
  else
    Window.ExposeClass = ExposeClass$1;

/**
 * @license
 * Copyright 2019 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const t$1=globalThis,e$2=t$1.ShadowRoot&&(void 0===t$1.ShadyCSS||t$1.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,s$2=Symbol(),o$3=new WeakMap;let n$2 = class n{constructor(t,e,o){if(this._$cssResult$=!0,o!==s$2)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e;}get styleSheet(){let t=this.o;const s=this.t;if(e$2&&void 0===t){const e=void 0!==s&&1===s.length;e&&(t=o$3.get(s)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),e&&o$3.set(s,t));}return t}toString(){return this.cssText}};const r$2=t=>new n$2("string"==typeof t?t:t+"",void 0,s$2),S$1=(s,o)=>{if(e$2)s.adoptedStyleSheets=o.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const e of o){const o=document.createElement("style"),n=t$1.litNonce;void 0!==n&&o.setAttribute("nonce",n),o.textContent=e.cssText,s.appendChild(o);}},c$2=e$2?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const s of t.cssRules)e+=s.cssText;return r$2(e)})(t):t;

/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */const{is:i$2,defineProperty:e$1,getOwnPropertyDescriptor:h$1,getOwnPropertyNames:r$1,getOwnPropertySymbols:o$2,getPrototypeOf:n$1}=Object,a$1=globalThis,c$1=a$1.trustedTypes,l$1=c$1?c$1.emptyScript:"",p$1=a$1.reactiveElementPolyfillSupport,d$1=(t,s)=>t,u$1={toAttribute(t,s){switch(s){case Boolean:t=t?l$1:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t);}return t},fromAttribute(t,s){let i=t;switch(s){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t);}catch(t){i=null;}}return i}},f$1=(t,s)=>!i$2(t,s),b={attribute:!0,type:String,converter:u$1,reflect:!1,useDefault:!1,hasChanged:f$1};Symbol.metadata??=Symbol("metadata"),a$1.litPropertyMetadata??=new WeakMap;let y$1 = class y extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t);}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,s=b){if(s.state&&(s.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((s=Object.create(s)).wrapped=!0),this.elementProperties.set(t,s),!s.noAccessor){const i=Symbol(),h=this.getPropertyDescriptor(t,i,s);void 0!==h&&e$1(this.prototype,t,h);}}static getPropertyDescriptor(t,s,i){const{get:e,set:r}=h$1(this.prototype,t)??{get(){return this[s]},set(t){this[s]=t;}};return {get:e,set(s){const h=e?.call(this);r?.call(this,s),this.requestUpdate(t,h,i);},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??b}static _$Ei(){if(this.hasOwnProperty(d$1("elementProperties")))return;const t=n$1(this);t.finalize(),void 0!==t.l&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties);}static finalize(){if(this.hasOwnProperty(d$1("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(d$1("properties"))){const t=this.properties,s=[...r$1(t),...o$2(t)];for(const i of s)this.createProperty(i,t[i]);}const t=this[Symbol.metadata];if(null!==t){const s=litPropertyMetadata.get(t);if(void 0!==s)for(const[t,i]of s)this.elementProperties.set(t,i);}this._$Eh=new Map;for(const[t,s]of this.elementProperties){const i=this._$Eu(t,s);void 0!==i&&this._$Eh.set(i,t);}this.elementStyles=this.finalizeStyles(this.styles);}static finalizeStyles(s){const i=[];if(Array.isArray(s)){const e=new Set(s.flat(1/0).reverse());for(const s of e)i.unshift(c$2(s));}else void 0!==s&&i.push(c$2(s));return i}static _$Eu(t,s){const i=s.attribute;return !1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev();}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this));}addController(t){(this._$EO??=new Set).add(t),void 0!==this.renderRoot&&this.isConnected&&t.hostConnected?.();}removeController(t){this._$EO?.delete(t);}_$E_(){const t=new Map,s=this.constructor.elementProperties;for(const i of s.keys())this.hasOwnProperty(i)&&(t.set(i,this[i]),delete this[i]);t.size>0&&(this._$Ep=t);}createRenderRoot(){const t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return S$1(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.());}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.());}attributeChangedCallback(t,s,i){this._$AK(t,i);}_$ET(t,s){const i=this.constructor.elementProperties.get(t),e=this.constructor._$Eu(t,i);if(void 0!==e&&!0===i.reflect){const h=(void 0!==i.converter?.toAttribute?i.converter:u$1).toAttribute(s,i.type);this._$Em=t,null==h?this.removeAttribute(e):this.setAttribute(e,h),this._$Em=null;}}_$AK(t,s){const i=this.constructor,e=i._$Eh.get(t);if(void 0!==e&&this._$Em!==e){const t=i.getPropertyOptions(e),h="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==t.converter?.fromAttribute?t.converter:u$1;this._$Em=e;const r=h.fromAttribute(s,t.type);this[e]=r??this._$Ej?.get(e)??r,this._$Em=null;}}requestUpdate(t,s,i,e=!1,h){if(void 0!==t){const r=this.constructor;if(!1===e&&(h=this[t]),i??=r.getPropertyOptions(t),!((i.hasChanged??f$1)(h,s)||i.useDefault&&i.reflect&&h===this._$Ej?.get(t)&&!this.hasAttribute(r._$Eu(t,i))))return;this.C(t,s,i);}!1===this.isUpdatePending&&(this._$ES=this._$EP());}C(t,s,{useDefault:i,reflect:e,wrapped:h},r){i&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,r??s??this[t]),!0!==h||void 0!==r)||(this._$AL.has(t)||(this.hasUpdated||i||(s=void 0),this._$AL.set(t,s)),!0===e&&this._$Em!==t&&(this._$Eq??=new Set).add(t));}async _$EP(){this.isUpdatePending=!0;try{await this._$ES;}catch(t){Promise.reject(t);}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[t,s]of this._$Ep)this[t]=s;this._$Ep=void 0;}const t=this.constructor.elementProperties;if(t.size>0)for(const[s,i]of t){const{wrapped:t}=i,e=this[s];!0!==t||this._$AL.has(s)||void 0===e||this.C(s,void 0,i,e);}}let t=!1;const s=this._$AL;try{t=this.shouldUpdate(s),t?(this.willUpdate(s),this._$EO?.forEach(t=>t.hostUpdate?.()),this.update(s)):this._$EM();}catch(s){throw t=!1,this._$EM(),s}t&&this._$AE(s);}willUpdate(t){}_$AE(t){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t);}_$EM(){this._$AL=new Map,this.isUpdatePending=!1;}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return !0}update(t){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM();}updated(t){}firstUpdated(t){}};y$1.elementStyles=[],y$1.shadowRootOptions={mode:"open"},y$1[d$1("elementProperties")]=new Map,y$1[d$1("finalized")]=new Map,p$1?.({ReactiveElement:y$1}),(a$1.reactiveElementVersions??=[]).push("2.1.2");

/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const t=globalThis,i$1=t=>t,s$1=t.trustedTypes,e=s$1?s$1.createPolicy("lit-html",{createHTML:t=>t}):void 0,h="$lit$",o$1=`lit$${Math.random().toFixed(9).slice(2)}$`,n="?"+o$1,r=`<${n}>`,l=document,c=()=>l.createComment(""),a=t=>null===t||"object"!=typeof t&&"function"!=typeof t,u=Array.isArray,d=t=>u(t)||"function"==typeof t?.[Symbol.iterator],f="[ \t\n\f\r]",v=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,_=/-->/g,m=/>/g,p=RegExp(`>|${f}(?:([^\\s"'>=/]+)(${f}*=${f}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),g=/'/g,$=/"/g,y=/^(?:script|style|textarea|title)$/i,E=Symbol.for("lit-noChange"),A=Symbol.for("lit-nothing"),C=new WeakMap,P=l.createTreeWalker(l,129);function V(t,i){if(!u(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==e?e.createHTML(i):i}const N=(t,i)=>{const s=t.length-1,e=[];let n,l=2===i?"<svg>":3===i?"<math>":"",c=v;for(let i=0;i<s;i++){const s=t[i];let a,u,d=-1,f=0;for(;f<s.length&&(c.lastIndex=f,u=c.exec(s),null!==u);)f=c.lastIndex,c===v?"!--"===u[1]?c=_:void 0!==u[1]?c=m:void 0!==u[2]?(y.test(u[2])&&(n=RegExp("</"+u[2],"g")),c=p):void 0!==u[3]&&(c=p):c===p?">"===u[0]?(c=n??v,d=-1):void 0===u[1]?d=-2:(d=c.lastIndex-u[2].length,a=u[1],c=void 0===u[3]?p:'"'===u[3]?$:g):c===$||c===g?c=p:c===_||c===m?c=v:(c=p,n=void 0);const x=c===p&&t[i+1].startsWith("/>")?" ":"";l+=c===v?s+r:d>=0?(e.push(a),s.slice(0,d)+h+s.slice(d)+o$1+x):s+o$1+(-2===d?i:x);}return [V(t,l+(t[s]||"<?>")+(2===i?"</svg>":3===i?"</math>":"")),e]};class S{constructor({strings:t,_$litType$:i},e){let r;this.parts=[];let l=0,a=0;const u=t.length-1,d=this.parts,[f,v]=N(t,i);if(this.el=S.createElement(f,e),P.currentNode=this.el.content,2===i||3===i){const t=this.el.content.firstChild;t.replaceWith(...t.childNodes);}for(;null!==(r=P.nextNode())&&d.length<u;){if(1===r.nodeType){if(r.hasAttributes())for(const t of r.getAttributeNames())if(t.endsWith(h)){const i=v[a++],s=r.getAttribute(t).split(o$1),e=/([.?@])?(.*)/.exec(i);d.push({type:1,index:l,name:e[2],strings:s,ctor:"."===e[1]?I:"?"===e[1]?L:"@"===e[1]?z:H}),r.removeAttribute(t);}else t.startsWith(o$1)&&(d.push({type:6,index:l}),r.removeAttribute(t));if(y.test(r.tagName)){const t=r.textContent.split(o$1),i=t.length-1;if(i>0){r.textContent=s$1?s$1.emptyScript:"";for(let s=0;s<i;s++)r.append(t[s],c()),P.nextNode(),d.push({type:2,index:++l});r.append(t[i],c());}}}else if(8===r.nodeType)if(r.data===n)d.push({type:2,index:l});else {let t=-1;for(;-1!==(t=r.data.indexOf(o$1,t+1));)d.push({type:7,index:l}),t+=o$1.length-1;}l++;}}static createElement(t,i){const s=l.createElement("template");return s.innerHTML=t,s}}function M(t,i,s=t,e){if(i===E)return i;let h=void 0!==e?s._$Co?.[e]:s._$Cl;const o=a(i)?void 0:i._$litDirective$;return h?.constructor!==o&&(h?._$AO?.(!1),void 0===o?h=void 0:(h=new o(t),h._$AT(t,s,e)),void 0!==e?(s._$Co??=[])[e]=h:s._$Cl=h),void 0!==h&&(i=M(t,h._$AS(t,i.values),h,e)),i}class R{constructor(t,i){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=i;}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){const{el:{content:i},parts:s}=this._$AD,e=(t?.creationScope??l).importNode(i,!0);P.currentNode=e;let h=P.nextNode(),o=0,n=0,r=s[0];for(;void 0!==r;){if(o===r.index){let i;2===r.type?i=new k(h,h.nextSibling,this,t):1===r.type?i=new r.ctor(h,r.name,r.strings,this,t):6===r.type&&(i=new Z(h,this,t)),this._$AV.push(i),r=s[++n];}o!==r?.index&&(h=P.nextNode(),o++);}return P.currentNode=l,e}p(t){let i=0;for(const s of this._$AV)void 0!==s&&(void 0!==s.strings?(s._$AI(t,s,i),i+=s.strings.length-2):s._$AI(t[i])),i++;}}class k{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,i,s,e){this.type=2,this._$AH=A,this._$AN=void 0,this._$AA=t,this._$AB=i,this._$AM=s,this.options=e,this._$Cv=e?.isConnected??!0;}get parentNode(){let t=this._$AA.parentNode;const i=this._$AM;return void 0!==i&&11===t?.nodeType&&(t=i.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,i=this){t=M(this,t,i),a(t)?t===A||null==t||""===t?(this._$AH!==A&&this._$AR(),this._$AH=A):t!==this._$AH&&t!==E&&this._(t):void 0!==t._$litType$?this.$(t):void 0!==t.nodeType?this.T(t):d(t)?this.k(t):this._(t);}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t));}_(t){this._$AH!==A&&a(this._$AH)?this._$AA.nextSibling.data=t:this.T(l.createTextNode(t)),this._$AH=t;}$(t){const{values:i,_$litType$:s}=t,e="number"==typeof s?this._$AC(t):(void 0===s.el&&(s.el=S.createElement(V(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===e)this._$AH.p(i);else {const t=new R(e,this),s=t.u(this.options);t.p(i),this.T(s),this._$AH=t;}}_$AC(t){let i=C.get(t.strings);return void 0===i&&C.set(t.strings,i=new S(t)),i}k(t){u(this._$AH)||(this._$AH=[],this._$AR());const i=this._$AH;let s,e=0;for(const h of t)e===i.length?i.push(s=new k(this.O(c()),this.O(c()),this,this.options)):s=i[e],s._$AI(h),e++;e<i.length&&(this._$AR(s&&s._$AB.nextSibling,e),i.length=e);}_$AR(t=this._$AA.nextSibling,s){for(this._$AP?.(!1,!0,s);t!==this._$AB;){const s=i$1(t).nextSibling;i$1(t).remove(),t=s;}}setConnected(t){void 0===this._$AM&&(this._$Cv=t,this._$AP?.(t));}}class H{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,i,s,e,h){this.type=1,this._$AH=A,this._$AN=void 0,this.element=t,this.name=i,this._$AM=e,this.options=h,s.length>2||""!==s[0]||""!==s[1]?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=A;}_$AI(t,i=this,s,e){const h=this.strings;let o=!1;if(void 0===h)t=M(this,t,i,0),o=!a(t)||t!==this._$AH&&t!==E,o&&(this._$AH=t);else {const e=t;let n,r;for(t=h[0],n=0;n<h.length-1;n++)r=M(this,e[s+n],i,n),r===E&&(r=this._$AH[n]),o||=!a(r)||r!==this._$AH[n],r===A?t=A:t!==A&&(t+=(r??"")+h[n+1]),this._$AH[n]=r;}o&&!e&&this.j(t);}j(t){t===A?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"");}}class I extends H{constructor(){super(...arguments),this.type=3;}j(t){this.element[this.name]=t===A?void 0:t;}}class L extends H{constructor(){super(...arguments),this.type=4;}j(t){this.element.toggleAttribute(this.name,!!t&&t!==A);}}class z extends H{constructor(t,i,s,e,h){super(t,i,s,e,h),this.type=5;}_$AI(t,i=this){if((t=M(this,t,i,0)??A)===E)return;const s=this._$AH,e=t===A&&s!==A||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,h=t!==A&&(s===A||e);e&&this.element.removeEventListener(this.name,this,s),h&&this.element.addEventListener(this.name,this,t),this._$AH=t;}handleEvent(t){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t);}}class Z{constructor(t,i,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=i,this.options=s;}get _$AU(){return this._$AM._$AU}_$AI(t){M(this,t);}}const B=t.litHtmlPolyfillSupport;B?.(S,k),(t.litHtmlVersions??=[]).push("3.3.2");const D=(t,i,s)=>{const e=s?.renderBefore??i;let h=e._$litPart$;if(void 0===h){const t=s?.renderBefore??null;e._$litPart$=h=new k(i.insertBefore(c(),t),t,void 0,s??{});}return h._$AI(t),h};

/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */const s=globalThis;class i extends y$1{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0;}createRenderRoot(){const t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){const r=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=D(r,this.renderRoot,this.renderOptions);}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0);}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1);}render(){return E}}i._$litElement$=!0,i["finalized"]=!0,s.litElementHydrateSupport?.({LitElement:i});const o=s.litElementPolyfillSupport;o?.({LitElement:i});(s.litElementVersions??=[]).push("4.2.2");

/**
 # Copyright (c) 2016-2018 The flatmax-elements Authors. All rights reserved.
 #
 # Redistribution and use in source and binary forms, with or without
 # modification, are permitted provided that the following conditions are
 # met:
 #
 #    * Redistributions of source code must retain the above copyright
 # notice, this list of conditions and the following disclaimer.
 #    * Redistributions in binary form must reproduce the above
 # copyright notice, this list of conditions and the following disclaimer
 # in the documentation and/or other materials provided with the
 # distribution.
 #    * Neither the name of Flatmax Pty Ltd nor the names of its
 # contributors may be used to endorse or promote products derived from
 # this software without specific prior written permission.
 #
 # THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 # "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 # LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 # A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 # OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 # SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 # LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 # DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 # THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 # (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 # OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */


Window.LitElement = i;

!function(e){if("object"==typeof exports&&"undefined"!=typeof module)module.exports=e();else if("function"==typeof define&&define.amd)define([],e);else {var t;t="undefined"!=typeof window?window:"undefined"!=typeof global?global:"undefined"!=typeof self?self:this,t.JRPC=e();}}(function(){return function e(t,o,i){function s(r,u){if(!o[r]){if(!t[r]){var l="function"==typeof require&&require;if(!u&&l)return l(r,!0);if(n)return n(r,!0);var a=new Error("Cannot find module '"+r+"'");throw a.code="MODULE_NOT_FOUND",a}var c=o[r]={exports:{}};t[r][0].call(c.exports,function(e){var o=t[r][1][e];return s(o?o:e)},c,c.exports,e,t,o,i);}return o[r].exports}for(var n="function"==typeof require&&require,r=0;r<i.length;r++)s(i[r]);return s}({1:[function(e,t,o){(function(o){/*! JRPC v3.1.0
 * <https://github.com/vphantom/js-jrpc>
 * Copyright 2016 Stéphane Lavergne
 * Free software under MIT License: <https://opensource.org/licenses/MIT> */
function i(e){this.active=!0,this.transmitter=null,this.remoteTimeout=6e4,this.localTimeout=0,this.serial=0,this.discardSerial=0,this.outbox={requests:[],responses:[]},this.inbox={},this.localTimers={},this.outTimers={},this.localComponents={"system.listComponents":!0,"system.extension.dual-batch":!0},this.remoteComponents={},this.exposed={},this.exposed["system.listComponents"]=function(e,t){return "object"==typeof e&&null!==e&&(this.remoteComponents=e,this.remoteComponents["system._upgraded"]=!0),t(null,this.localComponents)}.bind(this),this.exposed["system.extension.dual-batch"]=function(e,t){return t(null,!0)},"object"==typeof e&&("remoteTimeout"in e&&"number"==typeof e.remoteTimeout&&(this.remoteTimeout=1e3*e.remoteTimeout),"localTimeout"in e&&"number"==typeof e.localTimeout&&(this.localTimeout=1e3*e.localTimeout));}function s(){var e=this;return e.active=!1,e.transmitter=null,e.remoteTimeout=0,e.localTimeout=0,e.localComponents={},e.remoteComponents={},e.outbox.requests.length=0,e.outbox.responses.length=0,e.inbox={},e.exposed={},Object.keys(e.localTimers).forEach(function(t){clearTimeout(e.localTimers[t]),delete e.localTimers[t];}),Object.keys(e.outTimers).forEach(function(t){clearTimeout(e.outTimers[t]),delete e.outTimers[t];}),e}function n(e){var t,o,i=null,s={responses:[],requests:[]};if("function"!=typeof e&&(e=this.transmitter),!this.active||"function"!=typeof e)return this;if(t=this.outbox.responses.length,o=this.outbox.requests.length,t>0&&o>0&&"system.extension.dual-batch"in this.remoteComponents)s=i={responses:this.outbox.responses,requests:this.outbox.requests},this.outbox.responses=[],this.outbox.requests=[];else if(t>0)t>1?(s.responses=i=this.outbox.responses,this.outbox.responses=[]):s.responses.push(i=this.outbox.responses.pop());else {if(!(o>0))return this;o>1?(s.requests=i=this.outbox.requests,this.outbox.requests=[]):s.requests.push(i=this.outbox.requests.pop());}return setImmediate(e,JSON.stringify(i),u.bind(this,s)),this}function r(e){return this.transmitter=e,this.transmit()}function u(e,t){this.active&&t&&(e.responses.length>0&&Array.prototype.push.apply(this.outbox.responses,e.responses),e.requests.length>0&&Array.prototype.push.apply(this.outbox.requests,e.requests));}function l(e){var t=[],o=[];if(!this.active)return this;if("string"==typeof e)try{e=JSON.parse(e);}catch(i){return this}if(e.constructor===Array){if(0===e.length)return this;"string"==typeof e[0].method?t=e:o=e;}else "object"==typeof e&&("undefined"!=typeof e.requests&&"undefined"!=typeof e.responses?(t=e.requests,o=e.responses):"string"==typeof e.method?t.push(e):o.push(e));return o.forEach(m.bind(this)),t.forEach(h.bind(this)),this}function a(){return this.active?this.call("system.listComponents",this.localComponents,function(e,t){e||"object"!=typeof t||(this.remoteComponents=t,this.remoteComponents["system._upgraded"]=!0);}.bind(this)):this}function c(e,t,o){var i={jsonrpc:"2.0",method:e};return this.active?("function"==typeof t&&(o=t,t=null),"system._upgraded"in this.remoteComponents&&!(e in this.remoteComponents)?("function"==typeof o&&setImmediate(o,{code:-32601,message:"Unknown remote method"}),this):(this.serial++,i.id=this.serial,"object"==typeof t&&(i.params=t),"function"==typeof o&&(this.inbox[this.serial]=o),this.outbox.requests.push(i),this.transmit(),"function"!=typeof o?this:(this.remoteTimeout>0?this.outTimers[this.serial]=setTimeout(m.bind(this,{jsonrpc:"2.0",id:this.serial,error:{code:-1e3,message:"Timed out waiting for response"}},!0),this.remoteTimeout):this.outTimers[this.serial]=!0,this))):this}function m(e,t){var o=!1,i=null;this.active&&"id"in e&&e.id in this.outTimers&&(t===!0&&clearTimeout(this.outTimers[e.id]),delete this.outTimers[e.id],"id"in e&&e.id in this.inbox&&("error"in e?o=e.error:i=e.result,setImmediate(this.inbox[e.id],o,i),delete this.inbox[e.id]));}function p(e,t){var o;if(!this.active)return this;if("string"==typeof e)this.localComponents[e]=!0,this.exposed[e]=t;else if("object"==typeof e)for(o in e)e.hasOwnProperty(o)&&(this.localComponents[o]=!0,this.exposed[o]=e[o]);return this}function h(e){var t=null,o=null;if(this.active&&"object"==typeof e&&null!==e&&"string"==typeof e.jsonrpc&&"2.0"===e.jsonrpc){if(t="undefined"!=typeof e.id?e.id:null,"string"!=typeof e.method)return void(null!==t&&(this.localTimers[t]=!0,setImmediate(f.bind(this,t,-32600))));if(!(e.method in this.exposed))return void(null!==t&&(this.localTimers[t]=!0,setImmediate(f.bind(this,t,-32601))));if("params"in e){if("object"!=typeof e.params)return void(null!==t&&(this.localTimers[t]=!0,setImmediate(f.bind(this,t,-32602))));o=e.params;}null===t&&(this.discardSerial--,t=this.discardSerial),this.localTimeout>0?this.localTimers[t]=setTimeout(f.bind(this,t,{code:-1002,message:"Method handler timed out"},void 0,!0),this.localTimeout):this.localTimers[t]=!0,setImmediate(this.exposed[e.method],o,f.bind(this,t));}}function f(e,t,o,i){var s={jsonrpc:"2.0",id:e};this.active&&e in this.localTimers&&(i===!0&&clearTimeout(this.localTimers[e]),delete this.localTimers[e],null===e||0>e||("undefined"!=typeof t&&null!==t&&t!==!1?"number"==typeof t?s.error={code:t,message:"error"}:t===!0?s.error={code:-1,message:"error"}:"string"==typeof t?s.error={code:-1,message:t}:"object"==typeof t&&"code"in t&&"message"in t?s.error=t:s.error={code:-2,message:"error",data:t}:s.result=o,this.outbox.responses.push(s),this.transmit()));}o.setImmediate=e("timers").setImmediate,i.prototype.shutdown=s,i.prototype.call=c,i.prototype.notify=c,i.prototype.expose=p,i.prototype.upgrade=a,i.prototype.receive=l,i.prototype.transmit=n,i.prototype.setTransmitter=r,"function"==typeof Promise.promisify&&(i.prototype.callAsync=Promise.promisify(c)),t.exports=i;}).call(this,"undefined"!=typeof global?global:"undefined"!=typeof self?self:"undefined"!=typeof window?window:{});},{timers:3}],2:[function(e,t,o){function i(){c=!1,u.length?a=u.concat(a):m=-1,a.length&&s();}function s(){if(!c){var e=setTimeout(i);c=!0;for(var t=a.length;t;){for(u=a,a=[];++m<t;)u&&u[m].run();m=-1,t=a.length;}u=null,c=!1,clearTimeout(e);}}function n(e,t){this.fun=e,this.array=t;}function r(){}var u,l=t.exports={},a=[],c=!1,m=-1;l.nextTick=function(e){var t=new Array(arguments.length-1);if(arguments.length>1)for(var o=1;o<arguments.length;o++)t[o-1]=arguments[o];a.push(new n(e,t)),1!==a.length||c||setTimeout(s,0);},n.prototype.run=function(){this.fun.apply(null,this.array);},l.title="browser",l.browser=!0,l.env={},l.argv=[],l.version="",l.versions={},l.on=r,l.addListener=r,l.once=r,l.off=r,l.removeListener=r,l.removeAllListeners=r,l.emit=r,l.binding=function(e){throw new Error("process.binding is not supported")},l.cwd=function(){return "/"},l.chdir=function(e){throw new Error("process.chdir is not supported")},l.umask=function(){return 0};},{}],3:[function(e,t,o){function i(e,t){this._id=e,this._clearFn=t;}var s=e("process/browser.js").nextTick,n=Function.prototype.apply,r=Array.prototype.slice,u={},l=0;o.setTimeout=function(){return new i(n.call(setTimeout,window,arguments),clearTimeout)},o.setInterval=function(){return new i(n.call(setInterval,window,arguments),clearInterval)},o.clearTimeout=o.clearInterval=function(e){e.close();},i.prototype.unref=i.prototype.ref=function(){},i.prototype.close=function(){this._clearFn.call(window,this._id);},o.enroll=function(e,t){clearTimeout(e._idleTimeoutId),e._idleTimeout=t;},o.unenroll=function(e){clearTimeout(e._idleTimeoutId),e._idleTimeout=-1;},o._unrefActive=o.active=function(e){clearTimeout(e._idleTimeoutId);var t=e._idleTimeout;t>=0&&(e._idleTimeoutId=setTimeout(function(){e._onTimeout&&e._onTimeout();},t));},o.setImmediate="function"==typeof setImmediate?setImmediate:function(e){var t=l++,i=arguments.length<2?!1:r.call(arguments,1);return u[t]=!0,s(function(){u[t]&&(i?e.apply(null,i):e.call(null),o.clearImmediate(t));}),t},o.clearImmediate="function"==typeof clearImmediate?clearImmediate:function(e){delete u[e];};},{"process/browser.js":2}]},{},[1])(1)});

/**
 # Copyright (c) 2016-2018 The flatmax-elements Authors. All rights reserved.
 #
 # Redistribution and use in source and binary forms, with or without
 # modification, are permitted provided that the following conditions are
 # met:
 #
 #    * Redistributions of source code must retain the above copyright
 # notice, this list of conditions and the following disclaimer.
 #    * Redistributions in binary form must reproduce the above
 # copyright notice, this list of conditions and the following disclaimer
 # in the documentation and/or other materials provided with the
 # distribution.
 #    * Neither the name of Flatmax Pty Ltd nor the names of its
 # contributors may be used to endorse or promote products derived from
 # this software without specific prior written permission.
 #
 # THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 # "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 # LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 # A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 # OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 # SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 # LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 # DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 # THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 # (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 # OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */


Window.JRPC = JRPC;

/**
 # Copyright (c) 2016-2018 The flatmax-elements Authors. All rights reserved.
 #
 # Redistribution and use in source and binary forms, with or without
 # modification, are permitted provided that the following conditions are
 # met:
 #
 #    * Redistributions of source code must retain the above copyright
 # notice, this list of conditions and the following disclaimer.
 #    * Redistributions in binary form must reproduce the above
 # copyright notice, this list of conditions and the following disclaimer
 # in the documentation and/or other materials provided with the
 # distribution.
 #    * Neither the name of Flatmax Pty Ltd nor the names of its
 # contributors may be used to endorse or promote products derived from
 # this software without specific prior written permission.
 #
 # THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 # "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 # LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 # A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 # OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 # SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 # LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 # DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 # THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 # (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 # OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */


if (typeof module !== 'undefined' && typeof module.exports !== 'undefined'){  // nodejs
  var ExposeClass = ({});
  var crypto = require('crypto');
  var JRPC$1 = ({});
  var LitElement=class {};
} else {  // browser
  if (!crypto)
    var crypto = self.crypto;
  var ExposeClass = Window.ExposeClass;
  var LitElement = Window.LitElement; // load in the correct class for the browser
}

if (!crypto.randomUUID)
  crypto.randomUUID = ()=>{return crypto.getRandomValues(new Uint8Array(32)).toString('base64').replaceAll(',','');};

/** Call remotes in two different ways :
To call one remote :
  this.remote[uuid].rpcs[fnName](args)
  .then((...)=>{...})
  .catch(...)

To call all remotes :
  this.call[fnName](args)
  .then((...)=>{...})
  .catch(...)
*/
let JRPCCommon$1 = class JRPCCommon extends LitElement {
  /** Instansiate a new remote. It gets added to the array of remotes
  @return the new remote
  */
  newRemote(){
    let remote;
    if (typeof Window === 'undefined') // nodejs
      remote = new JRPC$1({ remoteTimeout: this.remoteTimeout }); // setup the remote
    else // browser
      remote = new Window.JRPC({ remoteTimeout: this.remoteTimeout }); // setup the remote
    remote.uuid = crypto.randomUUID();
    if (this.remotes==null)
      this.remotes = {};
    this.remotes[remote.uuid]=remote;
    return remote;
  }

  /** Function called by the WebSocket once 'connection' is fired
  \param ws The web socket created by the web socket server (in the case of node)
  */
  createRemote(ws){
    let remote = this.newRemote();
    this.remoteIsUp();

    if (this.ws) { // browser version of ws
      ws=this.ws;
      this.ws.onclose =  function (evMsg) {this.rmRemote(evMsg, remote.uuid);}.bind(this);
      this.ws.onmessage = (evMsg) => { remote.receive(evMsg.data); };
    } else { // node version of ws
      ws.on('close', (evMsg, buf)=>this.rmRemote.bind(this)(evMsg, remote.uuid));
      ws.on('message', function(data, isBinary) {
        const msg = isBinary ? data : data.toString(); // changes for upgrade to v8
        remote.receive(msg);
      });
    }

    this.setupRemote(remote, ws);
    return remote;
  }

  /** Overload this to execute code when the remote comes up
  */
  remoteIsUp() {
    console.log('JRPCCommon::remoteIsUp');
  }

  /** Remove the remote
  @param uuid The uuid of the remote to remove
  */
  rmRemote(e, uuid){
    // console.log(uuid)
    // console.log('before')
    // console.log(this.remotes)
    // console.log(this.server)

    // NOTE : this.server to be removed in the future.
    if (this.server) // remove the methods in the remote from the server
      if (this.remotes[uuid])
        if (this.remotes[uuid].rpcs)
          Object.keys(this.remotes[uuid].rpcs).forEach((fn) => {if (this.server[fn]) delete this.server[fn];});

    if (Object.keys(this.remotes).length)
      delete this.remotes[uuid];

    if (this.call && Object.keys(this.remotes).length){
      let remainingFns = [];
      for (const remote in this.remotes)
        if (this.remotes[remote].rpcs)
          remainingFns = remainingFns.concat(Object.keys(this.remotes[remote].rpcs));
      if (this.call) {
        let existingFns = Object.keys(this.call);
        for (let n=0; n<existingFns.length; n++)
          if (remainingFns.indexOf(existingFns[n]) < 0)
            delete this.call[existingFns[n]];
      }
    } else
      this.call={}; // reset the call all object

    this.remoteDisconnected(uuid);
    // console.log('after')
    // console.log('this.call after')
    // console.log(this.call)
    // console.log('this.remotes')
    // console.log(this.remotes)
    // console.log(this.server)
  }

  /** Notify that a remote has been disconnected
  @param uuid The uuid of the remote to remove
  */
  remoteDisconnected(uuid){
    console.log('JPRCCommon::remoteDisconnected '+uuid);
  }

  /** expose classes and handle the setting up of remote's functions
  @param remote the remote to setup
  @param ws the websocket for transmission
  */
  setupRemote(remote, ws){
    remote.setTransmitter(this.transmit.bind(ws)); // Let JRPC send requests and responses continuously
    if (this.classes)
      this.classes.forEach((c) => {
        remote.expose(c);
      });
    remote.upgrade();

    remote.call('system.listComponents', [], (err, result) => {
      if (err) {
        console.log(err);
        console.log('Something went wrong when calling system.listComponents !');
      } else // setup the functions for overloading
        this.setupFns(Object.keys(result), remote);
    });
  }

  /** Transmit a message or queue of messages to the server.
  Bind the web socket to this method for calling this.send
  @param msg the message to send
  @param next the next to execute
  */
  transmit(msg, next){
  	try {
  	  this.send(msg);
  	  return next(false);
  	} catch (e) {
      console.log(e);
  	  return next(true);
  	}
  }

  /** Setup functions for calling on the server. It allows you to call server['class.method'](args) in your code.
  The return values from the function call will execute this['class.method'](returnArgs) here.
  @param fnNames The functions to make available on the server
  @param remote The remote to call
  */
  setupFns(fnNames, remote){
     fnNames.forEach(fnName => {
      if (remote.rpcs==null) // each remote holds its own rpcs
        remote.rpcs={};

      // each remote's rpcs will hold the functino to call and returns a promise
      remote.rpcs[fnName] = function (params) {
        return new Promise((resolve, reject) => {
          remote.call(fnName, {args : Array.from(arguments)}, (err, result) => {
              if (err) {
                console.log('Error when calling remote function : '+fnName);
                reject(err);
              } else // resolve
                resolve(result);
          });
        });
      };

      // the call structure is to call all remotes
      if (this.call == null) // server holds all remote's rpcs
        this.call={};
      if (this.call[fnName]==null){ // first time in use
        this.call[fnName] = (...args) => {
            let promises = [];
            let rems = [];
            for (const remote in this.remotes){
              if (this.remotes[remote].rpcs[fnName] != null){ // store promises as [uuid : function, ...]
                rems.push(remote);
                promises.push(this.remotes[remote].rpcs[fnName](...args));
              }
            }
            return Promise.all(promises).then((data) => {
              let p = {};
              rems.forEach((v,n)=> p[v]=data[n]);
              return p;
            });
        };
      }

      //////////////////////////////////////////////////
      // For backwards compat - START TO BE REMOVED IN FUTURE
      // if server has a spare spot for that fnName, use it
      // otherwise error out in use (we don't know whot to talk to)
      if (this.server == null) // server holds all remote's rpcs
        this.server={};
      if (this.server[fnName]==null){ // first time in use
        // console.log(fnName+' not in server');
        // note this code should be the same as remote.rpcs[fnName]
        // replicating code here to ensure we don't mess with the orignal
        // remote.rpcs[fnNAme] reference if the else case is triggered in future
        this.server[fnName] = function (params) {
          return new Promise((resolve, reject) => {
            remote.call(fnName, {args : Array.from(arguments)}, (err, result) => {
                if (err) {
                  console.log('Error when calling remote function : '+fnName);
                  reject(err);
                } else // resolve
                  resolve(result);
            });
          });
        };
      } else { // some other remote already uses this fnName, error out
        // console.log(fnName+' in server, rejecting calls');
        this.server[fnName] = function (params) {
          return new Promise((resolve, reject) => {
            reject(new Error('More then one remote has this RPC, not sure who to talk to : '+fnName));
          });
        };
      }
      // For backwards compat - END TO BE REMOVED IN FUTURE
      //////////////////////////////////////////////////
    });

    this.setupDone();
  }

  /** This function is called once the client has been contacted and the server functions are
  set up.
  You should overload this function to get a notification once the 'server' variable is ready
  for use.
  */
  setupDone(){}

  /** Add a class to the JRPC system. All functions in the class are exposed for use.
  \param c The class to expose for use in the JRPC system.
  \param objName If name is specified, then use it rather then the constructor's name to prepend the functions.
  */
  addClass(c, objName){
    c.getRemotes = () => {return this.remotes;}; // give the class a method to get the remotes
    c.getCall = () => {return this.call;}; // give the class a method to get the call methods back to handle callbacks too all remotes
    // NOTE : getServer will be removed in future
    c.getServer = () => {return this.server;}; // give the class a method to get the server back to handle callbacks
    let exposeClass=new ExposeClass();
    let jrpcObj=exposeClass.exposeAllFns(c, objName); // get a js-JRPC friendly function object
    if (this.classes == null)
      this.classes = [jrpcObj];
    else
      this.classes.push(jrpcObj);

    if (this.remotes!=null) // update all existing remotes
      for (const [uuid, remote] of Object.entries(this.remotes)) {
        remote.expose(jrpcObj); // expose the functions from the class
        remote.upgrade();  // Handshake extended capabilities
      }

      // auto defining getters needs more work
      // if (!('remotes' in c))
      //   Object.defineProperty(c, 'remotes', {
      //     get() {return c.getRemotes();}
      //   });
      // if (!('call' in c))
      //   Object.defineProperty(c, 'call', {  // add a getter for the call local member variable
      //     get() {return c.getCall();},
      //     enumerable: true
      //   });
  }
};

if (typeof module !== 'undefined' && typeof module.exports !== 'undefined')
    module.exports = JRPCCommon$1;
  else
    Window.JRPCCommon = JRPCCommon$1;

/**
 # Copyright (c) 2016-2018 The flatmax-elements Authors. All rights reserved.
 #
 # Redistribution and use in source and binary forms, with or without
 # modification, are permitted provided that the following conditions are
 # met:
 #
 #    * Redistributions of source code must retain the above copyright
 # notice, this list of conditions and the following disclaimer.
 #    * Redistributions in binary form must reproduce the above
 # copyright notice, this list of conditions and the following disclaimer
 # in the documentation and/or other materials provided with the
 # distribution.
 #    * Neither the name of Flatmax Pty Ltd nor the names of its
 # contributors may be used to endorse or promote products derived from
 # this software without specific prior written permission.
 #
 # THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 # "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 # LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 # A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 # OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 # SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 # LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 # DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 # THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 # (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 # OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

let JRPCCommon = Window.JRPCCommon;

/**
  * `jrpc-client`
  * js-jrpc element
  * This element exposes all js-jrpc functions on a compliant server.
  * When the server responds to the first call upon connecting, local functions are
  * created which match the server's functions. If the local functions are called with
  * JSON params, then the server is called.
  * Inheriting parents must define the functions which the server exposes, which will
  * be called once the server responds.
  * @customElement
  * @litelement
  * @demo demo/index.html
  */
class JRPCClient extends JRPCCommon {
  static get properties() {
    return {
      serverURI: { type: String },
      ws: { type: Object }, // web socket
      server: { type: Object }, // server functions
      remoteTimeout: { type: Number }
    };
  }

  constructor() {
    super();
    this.remoteTimeout = 60;
  }

  updated(changedProps) {
    if (changedProps.has('serverURI')) {
      if (this.serverURI && this.serverURI != "undefined") {
        this.serverChanged();
      }
    }
  }

  /** When the serverIP is set, connect to the new server's websocket
  */
  serverChanged() {
    if (this.ws != null) // get rid of an old server
      delete this.ws;

    // Try to catch the error once ws init failed
    try {
      this.ws = new WebSocket(this.serverURI);
      // set the wss reference to this
      console.assert(this.ws.parent == null, 'wss.parent already exists, this needs upgrade.');
      this.ws.addEventListener('open', this.createRemote.bind(this));
      this.ws.addEventListener('error', this.wsError.bind(this));
    } catch (e) {
      this.serverURI = "";
      this.setupSkip(e);
    }
  }

  /** When a new websocket doesn't exists, return error
  */
  wsError(ev) {
    this.setupSkip(ev);
  }

  /** Report if we are connected to a server or not
  @return true if connected to a server
  */
  isConnected() {
    return this.server != null && this.server != {};
  }

  /** This function is called if the websocket is refused or gets an error
  */
  setupSkip() {
    this.dispatchEvent(new CustomEvent('skip'));
  }

  setupDone() {
    this.dispatchEvent(new CustomEvent('done'));
  }
}

if(!window.customElements.get('jrpc-client')) { window.customElements.define('jrpc-client', JRPCClient); }

export { JRPCClient };
