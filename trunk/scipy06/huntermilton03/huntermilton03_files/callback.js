/*****************************************************************************
 * javascript/entrez/callback.js
 *
 * Entrez Linking callback to populate content box.
 *
 * Copyright 2006 Board of Trustees of the Leland Stanford Junior University.
 ****************************************************************************/

/*
 * Execute callback to fill content box with Entrez Linking information.
 */
function entrez_callback(pmid, callback_url) {
  /*
   * MSIE 5.5 and below have issues with the JavaScript
   * used for Entrez Linking. For now we have to disable
   * the callback until we can track down a proper fix
   * (or everybody sanely upgrades to version 6 or 7!).
   */
  if (navigator) {
    var appname = navigator.appName;
    if (appname == "Microsoft Internet Explorer") {
      var userAgent = navigator["userAgent"];
      var s = "MSIE ";
      var n = -1;      
      if ((n = userAgent.indexOf(s)) != -1) {
        var v = parseFloat(userAgent.substring(n+s.length));
        if (v < 6) {
          return;
        }
      }
    }
  }

  /*
   * Acquire table row element to update, initiate callback
   * to update table with Entrez Links.
   */
  var tr = document.getElementById('entrez_callback_'+pmid);
  if (!tr) {
    return;
  }
  var req = new XMLHttpRequest();
  if (!req) {
    return;
  }
  req.onreadystatechange = function() {
    if (req.readyState == 4 && (req.status == 200 || req.status == 304)) {
      var src = req.responseXML.documentElement;
      var dst = document.createDocumentFragment();
      for (var i = 0; i < src.childNodes.length; i++) {
      	copy_xml_to_html(src.childNodes[i], dst);
      }
      var tbl = tr.parentNode;
      tbl.replaceChild(dst, tr);
    }
  }
  req.open('GET', callback_url, true);
  req.send(null);
}
