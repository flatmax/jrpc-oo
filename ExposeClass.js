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

"use strict";

/** Class to expose another class's methods for use with something like js-JRPC
*/
class ExposeClass {
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
    var me=this;
    fns.forEach(function (fnName){
      fnsExp[fnName]=function(params, next){
        Promise.resolve(classToExpose[fnName.substring(fnName.indexOf('.')+1)].apply(classToExpose, params.args))
        .then(function(ret){
          return next(null,ret);
        }).catch(function(err){
          console.log('failed : '+err)
          return next(err);
        });
      }
    })
    //console.log(fnsExp) // uncomment this to see which functions are being exposed.
    return fnsExp;
  }
}

if (typeof module !== 'undefined' && typeof module.exports !== 'undefined')
    module.exports = ExposeClass;
  else
    Window.ExposeClass = ExposeClass;
