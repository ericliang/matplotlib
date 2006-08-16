/*****************************************************************************
 * javascript/ajax/utility.js
 *
 * Utility functions for working with XMLHttpRequest data.
 *
 * Copyright 2006 Board of Trustees of the Leland Stanford Junior University.
 ****************************************************************************/

/*
 * Copy XML nodes into an HTMLElement. This effectively
 * clones XML markup which uses XHTML naming conventions
 * into an HTML DOM.
 */
function copy_xml_to_html(src, dst) {
  if (src.nodeType == 1) { /* Node.ELEMENT_NODE */
    var e = document.createElement(src.nodeName);
    for (var i = 0; i < src.childNodes.length; i++) {
	  copy_xml_to_html(src.childNodes[i], e);
    }
    for (var i = 0; i < src.attributes.length; i++) {
      var n = src.attributes[i].name;
      var v = unescape_xml_string(src.attributes[i].value);      
      e.setAttribute(n, v);
      if (n == "class") {
        e.className = v;
      }
      else if (n == "style") {
        set_css_style(v, e, "");
      }
    }
    dst.appendChild(e);
  }
  else if (src.nodeType == 3) { /* Node.TEXT_NODE */
    dst.appendChild(document.createTextNode(src.nodeValue));
  }
}

/* 
 * It is unclear that this is the right thing to be calling
 * from copy_xml_to_html, but it appears that Safari decides
 * to convert &amp; to the NCR &#35;, and then encodes that
 * NCR to &%26%2338;.  So, I'm going to treat the DOM Attr
 * value as a plain string, and run our XML string input
 * through the decoding routine below.
 */
function unescape_xml_string(s) {
  return s.replace(/&apos;/g, "'")
          .replace(/&#39;/g,  "'")
          .replace(/&quot;/g, "\"")
          .replace(/&#34;/g,  "\"")
          .replace(/&gt;/g,   ">")
          .replace(/&#62;/g,  ">")
          .replace(/&lt;/g,   "<")
          .replace(/&#60;/g,  "<")
          .replace(/&amp;/g,  "&")
          .replace(/&#38;/g,  "&");
}

/*
 * Parse set of CSS rules and apply them to an element.
 * This is quite horrifying, but I'm unable to determine
 * how else to handle this with IE 6.  FireFox and other
 * sane browsers let you simply set the style attribute
 * or use e.style.setProperty(rule, value, priority),
 * IE 6 appears to have neither of these capabilities..
 */
function set_css_style(css, e, priority) {
  var rules = css.split(";");
  for (var i = 0; i < rules.length; i++) {
    var nvpair = rules[i].split(":");
    if (nvpair.length == 2) {
      try {
        var name  = nvpair[0]; /* style attribute */
        var value = nvpair[1]; /* attribute value */
  
        /*
         * For each possible style attribute, set the
         * appropriate style property in the element.
         */
        if (name == "background") {
           e.style.background = value;
        }
        else if (name == "background-attachment") {
          e.style.backgroundAttachment = value;
        }
        else if (name == "background-color") {
          e.style.backgroundColor = value;
        }
        else if (name == "background-image") {
          e.style.backgroundImage = value;
        }
        else if (name == "background-position") {
          e.style.backgroundPosition = value;
        }
        else if (name == "background-position-x") {
          e.style.backgroundPositionX = value;
        }
        else if (name == "background-position-y") {
          e.style.backgroundPositionY = value;
        }
        else if (name == "background-repeat") {
          e.style.backgroundRepeat = value;
        }
        else if (name == "behavior") {
          e.style.behavior = value;
        }
        else if (name == "border") {
          e.style.border = value;
        }
        else if (name == "border-bottom") {
          e.style.borderBottom = value;
        }
        else if (name == "border-bottom-color") {
          e.style.borderBottomColor = value;
        }
        else if (name == "border-bottom-style") {
          e.style.borderBottomStyle = value;
        }
        else if (name == "border-bottom-width") {
          e.style.borderBottomWidth = value;
        }
        else if (name == "border-collapse") {
          e.style.borderCollapse = value;
        }
        else if (name == "border-color") {
          e.style.borderColor = value;
        }
        else if (name == "border-left") {
          e.style.borderLeft = value;
        }
        else if (name == "border-left-color") {
          e.style.borderLeftColor = value;
        }
        else if (name == "border-left-style") {
          e.style.borderLeftStyle = value;
        }
        else if (name == "border-left-width") {
          e.style.borderLeftWidth = value;
        }
        else if (name == "border-right") {
          e.style.borderRight = value;
        }
        else if (name == "border-right-color") {
          e.style.borderRightColor = value;
        }
        else if (name == "border-right-style") {
          e.style.borderRightStyle = value;
        }
        else if (name == "border-right-width") {
          e.style.borderRightWidth = value;
        }
        else if (name == "border-style") {
          e.style.borderStyle = value;
        }
        else if (name == "border-top") {
          e.style.borderTop = value;
        }
        else if (name == "border-top-color") {
          e.style.borderTopColor = value;
        }
        else if (name == "border-top-style") {
          e.style.borderTopStyle = value;
        }
        else if (name == "border-top-width") {
          e.style.borderTopWidth = value;
        }
        else if (name == "border-width") {
          e.style.borderWidth = value;
        }
        else if (name == "bottom") {
          e.style.bottom = value;
        }
        else if (name == "clear") {
          e.style.clear = value;
        }
        else if (name == "clip") {
          e.style.clip = value;
        }
        else if (name == "color") {
          e.style.color = value;
        }
        else if (name == "cssText") {
          e.style.Sets = value;
        }
        else if (name == "cursor") {
          e.style.cursor = value;
        }
        else if (name == "direction") {
          e.style.direction = value;
        }
        else if (name == "display") {
          e.style.display = value;
        }
        else if (name == "font") {
          e.style.font = value;
        }
        else if (name == "font-family") {
          e.style.fontFamily = value;
        }
        else if (name == "font-size") {
          e.style.fontSize = value;
        }
        else if (name == "font-style") {
          e.style.fontStyle = value;
        }
        else if (name == "font-variant") {
          e.style.fontVariant = value;
        }
        else if (name == "font-weight") {
          e.style.fontWeight = value;
        }
        else if (name == "height") {
          e.style.height = value;
        }
        else if (name == "ime-mode") {
          e.style.imeMode = value;
        }
        else if (name == "layout-flow") {
          e.style.layoutFlow = value;
        }
        else if (name == "layout-grid") {
          e.style.layoutGrid = value;
        }
        else if (name == "layout-grid-char") {
          e.style.layoutGridChar = value;
        }
        else if (name == "layout-grid-line") {
          e.style.layoutGridLine = value;
        }
        else if (name == "layout-grid-mode") {
          e.style.layoutGridMode = value;
        }
        else if (name == "layout-grid-type") {
          e.style.layoutGridType = value;
        }
        else if (name == "left") {
          e.style.left = value;
        }
        else if (name == "letter-spacing") {
          e.style.letterSpacing = value;
        }
        else if (name == "line-break") {
          e.style.lineBreak = value;
        }
        else if (name == "line-height") {
          e.style.lineHeight = value;
        }
        else if (name == "list-style") {
          e.style.listStyle = value;
        }
        else if (name == "list-style-image") {
          e.style.listStyleImage = value;
        }
        else if (name == "list-style-position") {
          e.style.listStylePosition = value;
        }
        else if (name == "list-style-type") {
          e.style.listStyleType = value;
        }
        else if (name == "margin") {
          e.style.margin = value;
        }
        else if (name == "margin-bottom") {
          e.style.marginBottom = value;
        }
        else if (name == "margin-left") {
          e.style.marginLeft = value;
        }
        else if (name == "margin-right") {
          e.style.marginRight = value;
        }
        else if (name == "margin-top") {
          e.style.marginTop = value;
        }
        else if (name == "min-height") {
          e.style.minHeight = value;
        }
        else if (name == "overflow") {
          e.style.overflow = value;
        }
        else if (name == "overflow-x") {
          e.style.overflowX = value;
        }
        else if (name == "overflow-y") {
          e.style.overflowY = value;
        }
        else if (name == "padding") {
          e.style.padding = value;
        }
        else if (name == "padding-bottom") {
          e.style.paddingBottom = value;
        }
        else if (name == "padding-left") {
          e.style.paddingLeft = value;
        }
        else if (name == "padding-right") {
          e.style.paddingRight = value;
        }
        else if (name == "padding-top") {
          e.style.paddingTop = value;
        }
        else if (name == "page-break-after") {
          e.style.pageBreakAfter = value;
        }
        else if (name == "page-break-before") {
          e.style.pageBreakBefore = value;
        }
        else if (name == "pixelBottom") {
          e.style.pixelBottom = value;
        }
        else if (name == "pixelHeight") {
          e.style.pixelHeight = value;
        }
        else if (name == "pixelLeft") {
          e.style.pixelLeft = value;
        }
        else if (name == "pixelRight") {
          e.style.pixelRight = value;
        }
        else if (name == "pixelTop") {
          e.style.pixelTop = value;
        }
        else if (name == "pixelWidth") {
          e.style.pixelWidth = value;
        }
        else if (name == "posBottom") {
          e.style.posBottom = value;
        }
        else if (name == "posHeight") {
          e.style.posHeight = value;
        }
        else if (name == "position") {
          e.style.position = value;
        }
        else if (name == "posLeft") {
          e.style.posLeft = value;
        }
        else if (name == "posRight") {
          e.style.posRight = value;
        }
        else if (name == "posTop") {
          e.style.posTop = value;
        }
        else if (name == "posWidth") {
          e.style.posWidth = value;
        }
        else if (name == "right") {
          e.style.right = value;
        }
        else if (name == "ruby-align") {
          e.style.rubyAlign = value;
        }
        else if (name == "ruby-overhang") {
          e.style.rubyOverhang = value;
        }
        else if (name == "ruby-position") {
          e.style.rubyPosition = value;
        }
        else if (name == "scrollbar-3dlight-color") {
          e.style.scrollbar3dLightColor = value;
        }
        else if (name == "scrollbar-arrow-color") {
          e.style.scrollbarArrowColor = value;
        }
        else if (name == "scrollbar-base-color") {
          e.style.scrollbarBaseColor = value;
        }
        else if (name == "scrollbar-darkshadow-color") {
          e.style.scrollbarDarkShadowColor = value;
        }
        else if (name == "scrollbar-face-color") {
          e.style.scrollbarFaceColor = value;
        }
        else if (name == "scrollbar-highlight-color") {
          e.style.scrollbarHighlightColor = value;
        }
        else if (name == "scrollbar-shadow-color") {
          e.style.scrollbarShadowColor = value;
        }
        else if (name == "scrollbar-track-color") {
          e.style.scrollbarTrackColor = value;
        }
        else if (name == "float") {
          e.style.styleFloat = value;
        }
        else if (name == "table-layout") {
          e.style.tableLayout = value;
        }
        else if (name == "text-align") {
          e.style.textAlign = value;
        }
        else if (name == "text-align-last") {
          e.style.textAlignLast = value;
        }
        else if (name == "text-autospace") {
          e.style.textAutospace = value;
        }
        else if (name == "text-decoration") {
          e.style.textDecoration = value;
        }
        else if (name == "textDecorationBlink") {
          e.style.textDecorationBlink = value;
        }
        else if (name == "textDecorationLineThrough") {
          e.style.textDecorationLineThrough = value;
        }
        else if (name == "textDecorationNone") {
          e.style.textDecorationNone = value;
        }
        else if (name == "textDecorationOverline") {
          e.style.textDecorationOverline = value;
        }
        else if (name == "textDecorationUnderline") {
          e.style.textDecorationUnderline = value;
        }
        else if (name == "text-indent") {
          e.style.textIndent = value;
        }
        else if (name == "text-justify") {
          e.style.textJustify = value;
        }
        else if (name == "text-kashida-space") {
          e.style.textKashidaSpace = value;
        }
        else if (name == "text-overflow") {
          e.style.textOverflow = value;
        }
        else if (name == "text-transform") {
          e.style.textTransform = value;
        }
        else if (name == "text-underline-position") {
          e.style.textUnderlinePosition = value;
        }
        else if (name == "top") {
          e.style.top = value;
        }
        else if (name == "unicode-bidi") {
          e.style.unicodeBidi = value;
        }
        else if (name == "vertical-align") {
          e.style.verticalAlign = value;
        }
        else if (name == "visibility") {
          e.style.visibility = value;
        }
        else if (name == "white-space") {
          e.style.whiteSpace = value;
        }
        else if (name == "width") {
          e.style.width = value;
        }
        else if (name == "word-break") {
          e.style.wordBreak = value;
        }
        else if (name == "word-spacing") {
          e.style.wordSpacing = value;
        }
        else if (name == "word-wrap") {
          e.style.wordWrap = value;
        }
        else if (name == "writing-mode") {
          e.style.writingMode = value;
        }
        else if (name == "z-index") {
          e.style.zIndex = value;
        }
        else if (name == "zoom") {
          e.style.zoom = value;
        }
      }
      catch (e) {
        /* ignore error on attempt to set e.style.[property] */
      }
    }
  }
}
