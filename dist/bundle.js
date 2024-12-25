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
const t$1=window,e$2=t$1.ShadowRoot&&(void 0===t$1.ShadyCSS||t$1.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,s$3=Symbol(),n$3=new WeakMap;let o$3 = class o{constructor(t,e,n){if(this._$cssResult$=!0,n!==s$3)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e;}get styleSheet(){let t=this.o;const s=this.t;if(e$2&&void 0===t){const e=void 0!==s&&1===s.length;e&&(t=n$3.get(s)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),e&&n$3.set(s,t));}return t}toString(){return this.cssText}};const r$2=t=>new o$3("string"==typeof t?t:t+"",void 0,s$3),S$1=(s,n)=>{e$2?s.adoptedStyleSheets=n.map((t=>t instanceof CSSStyleSheet?t:t.styleSheet)):n.forEach((e=>{const n=document.createElement("style"),o=t$1.litNonce;void 0!==o&&n.setAttribute("nonce",o),n.textContent=e.cssText,s.appendChild(n);}));},c$1=e$2?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const s of t.cssRules)e+=s.cssText;return r$2(e)})(t):t;

/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */var s$2;const e$1=window,r$1=e$1.trustedTypes,h$1=r$1?r$1.emptyScript:"",o$2=e$1.reactiveElementPolyfillSupport,n$2={toAttribute(t,i){switch(i){case Boolean:t=t?h$1:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t);}return t},fromAttribute(t,i){let s=t;switch(i){case Boolean:s=null!==t;break;case Number:s=null===t?null:Number(t);break;case Object:case Array:try{s=JSON.parse(t);}catch(t){s=null;}}return s}},a$1=(t,i)=>i!==t&&(i==i||t==t),l$2={attribute:!0,type:String,converter:n$2,reflect:!1,hasChanged:a$1},d$1="finalized";let u$1 = class u extends HTMLElement{constructor(){super(),this._$Ei=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$El=null,this._$Eu();}static addInitializer(t){var i;this.finalize(),(null!==(i=this.h)&&void 0!==i?i:this.h=[]).push(t);}static get observedAttributes(){this.finalize();const t=[];return this.elementProperties.forEach(((i,s)=>{const e=this._$Ep(s,i);void 0!==e&&(this._$Ev.set(e,s),t.push(e));})),t}static createProperty(t,i=l$2){if(i.state&&(i.attribute=!1),this.finalize(),this.elementProperties.set(t,i),!i.noAccessor&&!this.prototype.hasOwnProperty(t)){const s="symbol"==typeof t?Symbol():"__"+t,e=this.getPropertyDescriptor(t,s,i);void 0!==e&&Object.defineProperty(this.prototype,t,e);}}static getPropertyDescriptor(t,i,s){return {get(){return this[i]},set(e){const r=this[t];this[i]=e,this.requestUpdate(t,r,s);},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)||l$2}static finalize(){if(this.hasOwnProperty(d$1))return !1;this[d$1]=!0;const t=Object.getPrototypeOf(this);if(t.finalize(),void 0!==t.h&&(this.h=[...t.h]),this.elementProperties=new Map(t.elementProperties),this._$Ev=new Map,this.hasOwnProperty("properties")){const t=this.properties,i=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(const s of i)this.createProperty(s,t[s]);}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(i){const s=[];if(Array.isArray(i)){const e=new Set(i.flat(1/0).reverse());for(const i of e)s.unshift(c$1(i));}else void 0!==i&&s.push(c$1(i));return s}static _$Ep(t,i){const s=i.attribute;return !1===s?void 0:"string"==typeof s?s:"string"==typeof t?t.toLowerCase():void 0}_$Eu(){var t;this._$E_=new Promise((t=>this.enableUpdating=t)),this._$AL=new Map,this._$Eg(),this.requestUpdate(),null===(t=this.constructor.h)||void 0===t||t.forEach((t=>t(this)));}addController(t){var i,s;(null!==(i=this._$ES)&&void 0!==i?i:this._$ES=[]).push(t),void 0!==this.renderRoot&&this.isConnected&&(null===(s=t.hostConnected)||void 0===s||s.call(t));}removeController(t){var i;null===(i=this._$ES)||void 0===i||i.splice(this._$ES.indexOf(t)>>>0,1);}_$Eg(){this.constructor.elementProperties.forEach(((t,i)=>{this.hasOwnProperty(i)&&(this._$Ei.set(i,this[i]),delete this[i]);}));}createRenderRoot(){var t;const s=null!==(t=this.shadowRoot)&&void 0!==t?t:this.attachShadow(this.constructor.shadowRootOptions);return S$1(s,this.constructor.elementStyles),s}connectedCallback(){var t;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(t=this._$ES)||void 0===t||t.forEach((t=>{var i;return null===(i=t.hostConnected)||void 0===i?void 0:i.call(t)}));}enableUpdating(t){}disconnectedCallback(){var t;null===(t=this._$ES)||void 0===t||t.forEach((t=>{var i;return null===(i=t.hostDisconnected)||void 0===i?void 0:i.call(t)}));}attributeChangedCallback(t,i,s){this._$AK(t,s);}_$EO(t,i,s=l$2){var e;const r=this.constructor._$Ep(t,s);if(void 0!==r&&!0===s.reflect){const h=(void 0!==(null===(e=s.converter)||void 0===e?void 0:e.toAttribute)?s.converter:n$2).toAttribute(i,s.type);this._$El=t,null==h?this.removeAttribute(r):this.setAttribute(r,h),this._$El=null;}}_$AK(t,i){var s;const e=this.constructor,r=e._$Ev.get(t);if(void 0!==r&&this._$El!==r){const t=e.getPropertyOptions(r),h="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==(null===(s=t.converter)||void 0===s?void 0:s.fromAttribute)?t.converter:n$2;this._$El=r,this[r]=h.fromAttribute(i,t.type),this._$El=null;}}requestUpdate(t,i,s){let e=!0;void 0!==t&&(((s=s||this.constructor.getPropertyOptions(t)).hasChanged||a$1)(this[t],i)?(this._$AL.has(t)||this._$AL.set(t,i),!0===s.reflect&&this._$El!==t&&(void 0===this._$EC&&(this._$EC=new Map),this._$EC.set(t,s))):e=!1),!this.isUpdatePending&&e&&(this._$E_=this._$Ej());}async _$Ej(){this.isUpdatePending=!0;try{await this._$E_;}catch(t){Promise.reject(t);}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var t;if(!this.isUpdatePending)return;this.hasUpdated,this._$Ei&&(this._$Ei.forEach(((t,i)=>this[i]=t)),this._$Ei=void 0);let i=!1;const s=this._$AL;try{i=this.shouldUpdate(s),i?(this.willUpdate(s),null===(t=this._$ES)||void 0===t||t.forEach((t=>{var i;return null===(i=t.hostUpdate)||void 0===i?void 0:i.call(t)})),this.update(s)):this._$Ek();}catch(t){throw i=!1,this._$Ek(),t}i&&this._$AE(s);}willUpdate(t){}_$AE(t){var i;null===(i=this._$ES)||void 0===i||i.forEach((t=>{var i;return null===(i=t.hostUpdated)||void 0===i?void 0:i.call(t)})),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t);}_$Ek(){this._$AL=new Map,this.isUpdatePending=!1;}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$E_}shouldUpdate(t){return !0}update(t){void 0!==this._$EC&&(this._$EC.forEach(((t,i)=>this._$EO(i,this[i],t))),this._$EC=void 0),this._$Ek();}updated(t){}firstUpdated(t){}};u$1[d$1]=!0,u$1.elementProperties=new Map,u$1.elementStyles=[],u$1.shadowRootOptions={mode:"open"},null==o$2||o$2({ReactiveElement:u$1}),(null!==(s$2=e$1.reactiveElementVersions)&&void 0!==s$2?s$2:e$1.reactiveElementVersions=[]).push("1.6.3");

/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
var t;const i=window,s$1=i.trustedTypes,e=s$1?s$1.createPolicy("lit-html",{createHTML:t=>t}):void 0,o$1="$lit$",n$1=`lit$${(Math.random()+"").slice(9)}$`,l$1="?"+n$1,h=`<${l$1}>`,r=document,u=()=>r.createComment(""),d=t=>null===t||"object"!=typeof t&&"function"!=typeof t,c=Array.isArray,v=t=>c(t)||"function"==typeof(null==t?void 0:t[Symbol.iterator]),a="[ \t\n\f\r]",f=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,_=/-->/g,m=/>/g,p=RegExp(`>|${a}(?:([^\\s"'>=/]+)(${a}*=${a}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),g=/'/g,$=/"/g,y=/^(?:script|style|textarea|title)$/i,T=Symbol.for("lit-noChange"),A=Symbol.for("lit-nothing"),E=new WeakMap,C=r.createTreeWalker(r,129,null,!1);function P(t,i){if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==e?e.createHTML(i):i}const V=(t,i)=>{const s=t.length-1,e=[];let l,r=2===i?"<svg>":"",u=f;for(let i=0;i<s;i++){const s=t[i];let d,c,v=-1,a=0;for(;a<s.length&&(u.lastIndex=a,c=u.exec(s),null!==c);)a=u.lastIndex,u===f?"!--"===c[1]?u=_:void 0!==c[1]?u=m:void 0!==c[2]?(y.test(c[2])&&(l=RegExp("</"+c[2],"g")),u=p):void 0!==c[3]&&(u=p):u===p?">"===c[0]?(u=null!=l?l:f,v=-1):void 0===c[1]?v=-2:(v=u.lastIndex-c[2].length,d=c[1],u=void 0===c[3]?p:'"'===c[3]?$:g):u===$||u===g?u=p:u===_||u===m?u=f:(u=p,l=void 0);const w=u===p&&t[i+1].startsWith("/>")?" ":"";r+=u===f?s+h:v>=0?(e.push(d),s.slice(0,v)+o$1+s.slice(v)+n$1+w):s+n$1+(-2===v?(e.push(void 0),i):w);}return [P(t,r+(t[s]||"<?>")+(2===i?"</svg>":"")),e]};class N{constructor({strings:t,_$litType$:i},e){let h;this.parts=[];let r=0,d=0;const c=t.length-1,v=this.parts,[a,f]=V(t,i);if(this.el=N.createElement(a,e),C.currentNode=this.el.content,2===i){const t=this.el.content,i=t.firstChild;i.remove(),t.append(...i.childNodes);}for(;null!==(h=C.nextNode())&&v.length<c;){if(1===h.nodeType){if(h.hasAttributes()){const t=[];for(const i of h.getAttributeNames())if(i.endsWith(o$1)||i.startsWith(n$1)){const s=f[d++];if(t.push(i),void 0!==s){const t=h.getAttribute(s.toLowerCase()+o$1).split(n$1),i=/([.?@])?(.*)/.exec(s);v.push({type:1,index:r,name:i[2],strings:t,ctor:"."===i[1]?H:"?"===i[1]?L:"@"===i[1]?z:k});}else v.push({type:6,index:r});}for(const i of t)h.removeAttribute(i);}if(y.test(h.tagName)){const t=h.textContent.split(n$1),i=t.length-1;if(i>0){h.textContent=s$1?s$1.emptyScript:"";for(let s=0;s<i;s++)h.append(t[s],u()),C.nextNode(),v.push({type:2,index:++r});h.append(t[i],u());}}}else if(8===h.nodeType)if(h.data===l$1)v.push({type:2,index:r});else {let t=-1;for(;-1!==(t=h.data.indexOf(n$1,t+1));)v.push({type:7,index:r}),t+=n$1.length-1;}r++;}}static createElement(t,i){const s=r.createElement("template");return s.innerHTML=t,s}}function S(t,i,s=t,e){var o,n,l,h;if(i===T)return i;let r=void 0!==e?null===(o=s._$Co)||void 0===o?void 0:o[e]:s._$Cl;const u=d(i)?void 0:i._$litDirective$;return (null==r?void 0:r.constructor)!==u&&(null===(n=null==r?void 0:r._$AO)||void 0===n||n.call(r,!1),void 0===u?r=void 0:(r=new u(t),r._$AT(t,s,e)),void 0!==e?(null!==(l=(h=s)._$Co)&&void 0!==l?l:h._$Co=[])[e]=r:s._$Cl=r),void 0!==r&&(i=S(t,r._$AS(t,i.values),r,e)),i}class M{constructor(t,i){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=i;}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){var i;const{el:{content:s},parts:e}=this._$AD,o=(null!==(i=null==t?void 0:t.creationScope)&&void 0!==i?i:r).importNode(s,!0);C.currentNode=o;let n=C.nextNode(),l=0,h=0,u=e[0];for(;void 0!==u;){if(l===u.index){let i;2===u.type?i=new R(n,n.nextSibling,this,t):1===u.type?i=new u.ctor(n,u.name,u.strings,this,t):6===u.type&&(i=new Z(n,this,t)),this._$AV.push(i),u=e[++h];}l!==(null==u?void 0:u.index)&&(n=C.nextNode(),l++);}return C.currentNode=r,o}v(t){let i=0;for(const s of this._$AV)void 0!==s&&(void 0!==s.strings?(s._$AI(t,s,i),i+=s.strings.length-2):s._$AI(t[i])),i++;}}class R{constructor(t,i,s,e){var o;this.type=2,this._$AH=A,this._$AN=void 0,this._$AA=t,this._$AB=i,this._$AM=s,this.options=e,this._$Cp=null===(o=null==e?void 0:e.isConnected)||void 0===o||o;}get _$AU(){var t,i;return null!==(i=null===(t=this._$AM)||void 0===t?void 0:t._$AU)&&void 0!==i?i:this._$Cp}get parentNode(){let t=this._$AA.parentNode;const i=this._$AM;return void 0!==i&&11===(null==t?void 0:t.nodeType)&&(t=i.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,i=this){t=S(this,t,i),d(t)?t===A||null==t||""===t?(this._$AH!==A&&this._$AR(),this._$AH=A):t!==this._$AH&&t!==T&&this._(t):void 0!==t._$litType$?this.g(t):void 0!==t.nodeType?this.$(t):v(t)?this.T(t):this._(t);}k(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}$(t){this._$AH!==t&&(this._$AR(),this._$AH=this.k(t));}_(t){this._$AH!==A&&d(this._$AH)?this._$AA.nextSibling.data=t:this.$(r.createTextNode(t)),this._$AH=t;}g(t){var i;const{values:s,_$litType$:e}=t,o="number"==typeof e?this._$AC(t):(void 0===e.el&&(e.el=N.createElement(P(e.h,e.h[0]),this.options)),e);if((null===(i=this._$AH)||void 0===i?void 0:i._$AD)===o)this._$AH.v(s);else {const t=new M(o,this),i=t.u(this.options);t.v(s),this.$(i),this._$AH=t;}}_$AC(t){let i=E.get(t.strings);return void 0===i&&E.set(t.strings,i=new N(t)),i}T(t){c(this._$AH)||(this._$AH=[],this._$AR());const i=this._$AH;let s,e=0;for(const o of t)e===i.length?i.push(s=new R(this.k(u()),this.k(u()),this,this.options)):s=i[e],s._$AI(o),e++;e<i.length&&(this._$AR(s&&s._$AB.nextSibling,e),i.length=e);}_$AR(t=this._$AA.nextSibling,i){var s;for(null===(s=this._$AP)||void 0===s||s.call(this,!1,!0,i);t&&t!==this._$AB;){const i=t.nextSibling;t.remove(),t=i;}}setConnected(t){var i;void 0===this._$AM&&(this._$Cp=t,null===(i=this._$AP)||void 0===i||i.call(this,t));}}class k{constructor(t,i,s,e,o){this.type=1,this._$AH=A,this._$AN=void 0,this.element=t,this.name=i,this._$AM=e,this.options=o,s.length>2||""!==s[0]||""!==s[1]?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=A;}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(t,i=this,s,e){const o=this.strings;let n=!1;if(void 0===o)t=S(this,t,i,0),n=!d(t)||t!==this._$AH&&t!==T,n&&(this._$AH=t);else {const e=t;let l,h;for(t=o[0],l=0;l<o.length-1;l++)h=S(this,e[s+l],i,l),h===T&&(h=this._$AH[l]),n||(n=!d(h)||h!==this._$AH[l]),h===A?t=A:t!==A&&(t+=(null!=h?h:"")+o[l+1]),this._$AH[l]=h;}n&&!e&&this.j(t);}j(t){t===A?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=t?t:"");}}class H extends k{constructor(){super(...arguments),this.type=3;}j(t){this.element[this.name]=t===A?void 0:t;}}const I=s$1?s$1.emptyScript:"";class L extends k{constructor(){super(...arguments),this.type=4;}j(t){t&&t!==A?this.element.setAttribute(this.name,I):this.element.removeAttribute(this.name);}}class z extends k{constructor(t,i,s,e,o){super(t,i,s,e,o),this.type=5;}_$AI(t,i=this){var s;if((t=null!==(s=S(this,t,i,0))&&void 0!==s?s:A)===T)return;const e=this._$AH,o=t===A&&e!==A||t.capture!==e.capture||t.once!==e.once||t.passive!==e.passive,n=t!==A&&(e===A||o);o&&this.element.removeEventListener(this.name,this,e),n&&this.element.addEventListener(this.name,this,t),this._$AH=t;}handleEvent(t){var i,s;"function"==typeof this._$AH?this._$AH.call(null!==(s=null===(i=this.options)||void 0===i?void 0:i.host)&&void 0!==s?s:this.element,t):this._$AH.handleEvent(t);}}class Z{constructor(t,i,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=i,this.options=s;}get _$AU(){return this._$AM._$AU}_$AI(t){S(this,t);}}const B=i.litHtmlPolyfillSupport;null==B||B(N,R),(null!==(t=i.litHtmlVersions)&&void 0!==t?t:i.litHtmlVersions=[]).push("2.8.0");const D=(t,i,s)=>{var e,o;const n=null!==(e=null==s?void 0:s.renderBefore)&&void 0!==e?e:i;let l=n._$litPart$;if(void 0===l){const t=null!==(o=null==s?void 0:s.renderBefore)&&void 0!==o?o:null;n._$litPart$=l=new R(i.insertBefore(u(),t),t,void 0,null!=s?s:{});}return l._$AI(t),l};

/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */var l,o;class s extends u$1{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0;}createRenderRoot(){var t,e;const i=super.createRenderRoot();return null!==(t=(e=this.renderOptions).renderBefore)&&void 0!==t||(e.renderBefore=i.firstChild),i}update(t){const i=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=D(i,this.renderRoot,this.renderOptions);}connectedCallback(){var t;super.connectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!0);}disconnectedCallback(){var t;super.disconnectedCallback(),null===(t=this._$Do)||void 0===t||t.setConnected(!1);}render(){return T}}s.finalized=!0,s._$litElement$=!0,null===(l=globalThis.litElementHydrateSupport)||void 0===l||l.call(globalThis,{LitElement:s});const n=globalThis.litElementPolyfillSupport;null==n||n({LitElement:s});(null!==(o=globalThis.litElementVersions)&&void 0!==o?o:globalThis.litElementVersions=[]).push("3.3.3");

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


Window.LitElement = s;

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
  var ExposeClass = require("./ExposeClass.js");
  var crypto = require('crypto');
  var JRPC$1 = require('jrpc');
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
