// Copyright 2024   Gi Tae Cho

//    Licensed under the Apache License, Version 2.0 (the "License");
//    you may not use this file except in compliance with the License.
//    You may obtain a copy of the License at

//        http://www.apache.org/licenses/LICENSE-2.0

//    Unless required by applicable law or agreed to in writing, software
//    distributed under the License is distributed on an "AS IS" BASIS,
//    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//    See the License for the specific language governing permissions and
//    limitations under the License.


let aIds = [ "intro", "install", "getStarted", "network", "simulation", "resultAnalysis", "troubleshooting", "conclusion", "help" ];
let initialPageIx = -1; // -1 for the intro, but it will be replaced as soon as the caller html is loaded.
let bOpenAllClicked = true;
let bOpenAllTopClicked = true;
var lastItem;
var lastIx;
var aboutSmhCtrl;

var InitShowNavElement= function() {
    lastItem = 0;
    lastIx = 0;
    aboutSmhCtrl = false;
}

// This function doesn't use jQuery. It shows the selected item on the navigation panel on the left.
// It also gets the selected Navigation menu toggled.
function showNavElement(item, arrayIds) {        
    if( item < 0 ) {
        var lId;
        let id;
        var ix = item * -1;
        
        if(aboutSmhCtrl === false) {
            document.getElementById('highlight').hidden = true;
            aboutSmhCtrl = true;
        }
        
        //if(item !== lastItem) {
            if( lastItem !== 0) lId = arrayIds[(lastItem + 1) * (-1)];
        //}
        
        // added outer 'if-else' statement to get the selected menu on the 'nav' toggled.
        if(item !== lastItem) {
            id = arrayIds[(item + 1) * (-1)];
            lastItem = item;
        } else {
            lastItem = 0;
            document.getElementById('highlight').hidden = false;
            aboutSmhCtrl = false;
        }
        
        if(lId !== undefined) {
            document.getElementById(lId).hidden = true;
            if(lastIx !== 0) document.getElementById('m' + lastIx.toString()).classList.remove('sel');
        }
        
        if(id !== undefined) {
            document.getElementById(id).hidden = false;
            if(ix !== 0) document.getElementById('m' + ix.toString()).classList.add('sel');
            lastIx = ix;
        }
        
        // if( item === -9 ) { // It is "9. Help"
        //     document.getElementById("openCloseAll").disabled = true; // 'details' in the 'Help' page belongs to the top html file, so it cannot be
        // } else {
        //     document.getElementById("openCloseAll").disabled = false;
        // }
    } //else if(item === 1) el1 = true;
}

// following new 'showElement' function doesn't use jQuery.
function showElement(item) {
    showNavElement(item, aIds);
}

function openOrCloseAll(bTopOnly) {
    let div = document.getElementsByTagName("div");
    
    for(let i = 0; i < div.length; i++ ) {
        if(div[i].hidden === false) {

            if( div[i].id === "help") { // 'details' tags in the 'Help' page belongs to the top html file, not one in iframe.
                let dt = document.getElementsByTagName('details');
                for( let i = 0; i < dt.length; i++ ) {
                    if( bTopOnly === true ) { // open/close details only on top layer.
                        //if( dt[i].parentElement.parentElement.tagName === "BODY" ) {
                        if( dt[i].parentElement.parentElement.tagName === "SECTION" ) {
                            dt[i].open = bOpenAllTopClicked;
                        }
                    } else {
                        dt[i].open = bOpenAllClicked;
                    }
                }

                if( bTopOnly === true ) {
                    if( bOpenAllTopClicked === true ) {
                        document.getElementById("openCloseAllTop").innerText = "Close All Top";
                    } else {
                        document.getElementById("openCloseAllTop").innerText = "Open All Top";
                    }                    
                    bOpenAllTopClicked = !bOpenAllTopClicked;

                } else {
                    if( bOpenAllClicked === true ) {
                        document.getElementById("openCloseAll").innerText = "Close All";
                    } else {
                        document.getElementById("openCloseAll").innerText = "Open All";
                    }
                    bOpenAllClicked = !bOpenAllClicked;
                }

            } else {
                let ifr = div[i].getElementsByTagName("iframe");
                //let str = ifr.split("?");
                //ifr.src = str[0] + "?OpenAll=" + bOpen.toString();            
                if(ifr.length > 0 ) {
                    let bHtm = ifr[0].src.includes(".htm"); // to make sure it contains .htm file.
                    if( bHtm === true ) { // it contains .htm.
                        if( bTopOnly === true ) {
                            if( bOpenAllTopClicked === true ) {
                                ifr[0].contentWindow.postMessage( {msg: "openAllTop"}, "*");
                                document.getElementById("openCloseAllTop").innerText = "Close All Top";
                            } else {
                                ifr[0].contentWindow.postMessage( {msg: "closeAllTop"}, "*");
                                document.getElementById("openCloseAllTop").innerText = "Open All Top";
                            } 

                            bOpenAllTopClicked = !bOpenAllTopClicked;
                        } else {
                            if( bOpenAllClicked === true ) {
                                ifr[0].contentWindow.postMessage( {msg: "openAll"}, "*");
                                document.getElementById("openCloseAll").innerText = "Close All";
                            } else {
                                ifr[0].contentWindow.postMessage( {msg: "closeAll"}, "*");
                                document.getElementById("openCloseAll").innerText = "Open All";
                            }

                            bOpenAllClicked = !bOpenAllClicked;
                        }
                        break;
                    }
                }
            }
        }
    }
}


window.onload = function () {
    var rgb, rgbTxt, rlt, s, v;
    let ix = 0;
    let color = ["<span class='r'>", "<span class='g'>", "<span class='b'>"];
    //var smry, u;

    InitShowNavElement();
    // smry = document.getElementsByTagName("summary");

    // for( let i = 0; i < smry.length; i++ ) {
    //     u = smry[i].getElementsByTagName("u");
    //     if( u.length > 0 ) u[0].classList = "dtSummary";
    // }

    //window.addEventListener("message", topEventHandler);

    rgb = document.getElementsByClassName("rgb");
    for( let i = 0; i < rgb.length; i++ ) {
        rgbTxt = rgb[i].innerHTML.split("-&gt;");
        rlt = '';
        for( let j = 0; j < rgbTxt.length; j++ ) {
            s = '';
            for( let k = 0, ix = 0; k < rgbTxt[j].length; k++ ) {
                v = rgbTxt[j].at(k);
                if( v == "1" ) {
                    //s += '<span class="r">O</span>';
                    s += color[ix] + "&nbsp;O&nbsp;</span>";
                    ix++;
                } else if( v == "0" ) {
                    s += "<span class='fg'>&nbsp;O&nbsp;</span>";
                    ix++;
                }
            }

            //if((j+1) < rgbTxt.length ) s += "<br/> "; //" =&gt;<br/> ";
            ////else if ( j > 0 ) s += "&emsp;&ensp;";
            
            // if( rgbTxt.length == 1) {
            //     rlt += "&emsp;" + s;
            // } else {
            //     rlt += "<span class='fgn'>" + (j+1).toString() + ".</span>&nbsp;" + s;
            // }

            // if((j+1) < rgbTxt.length ) rlt += "<br/>";
            rlt += s;
            if((j+1) < rgbTxt.length ) rlt += "<br/>";
        }
        rgb[i].innerHTML = rlt;
    }

    if( initialPageIx !== 0 ) {
        showElement(initialPageIx);    // to show the command list page as the default.
    }
}