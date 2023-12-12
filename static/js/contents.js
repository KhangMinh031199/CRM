import React, {StyleSheet, Dimensions, PixelRatio} from "react-native";
const {width, height, scale} = Dimensions.get("window"),
    vw = width / 100,
    vh = height / 100,
    vmin = Math.min(vw, vh),
    vmax = Math.max(vw, vh);

export default StyleSheet.create({
    "cke_editable": {
        "fontSize": 13,
        "lineHeight": 1.6,
        "wordWrap": "break-word"
    },
    "blockquote": {
        "fontStyle": "italic",
        "fontFamily": "Georgia, Times, \"Times New Roman\", serif",
        "paddingTop": 2,
        "paddingRight": 0,
        "paddingBottom": 2,
        "paddingLeft": 0,
        "borderStyle": "solid",
        "borderColor": "#ccc",
        "borderWidth": 0
    },
    "cke_contents_ltr blockquote": {
        "paddingLeft": 20,
        "paddingRight": 8,
        "borderLeftWidth": 5
    },
    "cke_contents_rtl blockquote": {
        "paddingLeft": 8,
        "paddingRight": 20,
        "borderRightWidth": 5
    },
    "a": {
        "color": "#0782C1"
    },
    "ol": {
        "MarginRight": 0,
        "paddingTop": 0,
        "paddingRight": 40,
        "paddingBottom": 0,
        "paddingLeft": 40
    },
    "ul": {
        "MarginRight": 0,
        "paddingTop": 0,
        "paddingRight": 40,
        "paddingBottom": 0,
        "paddingLeft": 40
    },
    "dl": {
        "MarginRight": 0,
        "paddingTop": 0,
        "paddingRight": 40,
        "paddingBottom": 0,
        "paddingLeft": 40
    },
    "h1": {
        "fontWeight": "normal",
        "lineHeight": 1.2
    },
    "h2": {
        "fontWeight": "normal",
        "lineHeight": 1.2
    },
    "h3": {
        "fontWeight": "normal",
        "lineHeight": 1.2
    },
    "h4": {
        "fontWeight": "normal",
        "lineHeight": 1.2
    },
    "h5": {
        "fontWeight": "normal",
        "lineHeight": 1.2
    },
    "h6": {
        "fontWeight": "normal",
        "lineHeight": 1.2
    },
    "hr": {
        "border": 0,
        "borderTop": "1px solid #ccc"
    },
    "imgright": {
        "border": "1px solid #ccc",
        "float": "right",
        "marginLeft": 15,
        "paddingTop": 5,
        "paddingRight": 5,
        "paddingBottom": 5,
        "paddingLeft": 5
    },
    "imgleft": {
        "border": "1px solid #ccc",
        "float": "left",
        "marginRight": 15,
        "paddingTop": 5,
        "paddingRight": 5,
        "paddingBottom": 5,
        "paddingLeft": 5
    },
    "pre": {
        "whiteSpace": "pre-wrap",
        "wordWrap": "break-word",
        "MozTabSize": 4,
        "tabSize": 4
    },
    "marker": {
        "backgroundColor": "Yellow"
    },
    "span[lang]": {
        "fontStyle": "italic"
    },
    "figure": {
        "textAlign": "center",
        "border": "solid 1px #ccc",
        "borderRadius": 2,
        "background": "rgba(0,0,0,0.05)",
        "paddingTop": 10,
        "paddingRight": 10,
        "paddingBottom": 10,
        "paddingLeft": 10,
        "marginTop": 10,
        "marginRight": 20,
        "marginBottom": 10,
        "marginLeft": 20,
        "display": "inline-block"
    },
    "figure > figcaption": {
        "textAlign": "center",
        "display": "block"
    },
    "a > img": {
        "paddingTop": 1,
        "paddingRight": 1,
        "paddingBottom": 1,
        "paddingLeft": 1,
        "marginTop": 1,
        "marginRight": 1,
        "marginBottom": 1,
        "marginLeft": 1,
        "border": "none",
        "outline": "1px solid #0782C1"
    },
    "code-featured": {
        "border": "5px solid red"
    },
    "math-featured": {
        "paddingTop": 20,
        "paddingRight": 20,
        "paddingBottom": 20,
        "paddingLeft": 20,
        "boxShadow": "0 0 2px rgba(200, 0, 0, 1)",
        "backgroundColor": "rgba(255, 0, 0, 0.05)",
        "marginTop": 10,
        "marginRight": 10,
        "marginBottom": 10,
        "marginLeft": 10
    },
    "image-clean": {
        "border": 0,
        "background": "none",
        "paddingTop": 0,
        "paddingRight": 0,
        "paddingBottom": 0,
        "paddingLeft": 0
    },
    "image-clean > figcaption": {
        "fontSize": 0.9,
        "textAlign": "right"
    },
    "image-grayscale": {
        "backgroundColor": "white",
        "color": "#666"
    },
    "image-grayscale img": {
        "filter": "grayscale(100%)"
    },
    "imgimage-grayscale": {
        "filter": "grayscale(100%)"
    },
    "embed-240p": {
        "maxWidth": 426,
        "maxHeight": 240,
        "marginTop": 0,
        "marginRight": "auto",
        "marginBottom": 0,
        "marginLeft": "auto"
    },
    "embed-360p": {
        "maxWidth": 640,
        "maxHeight": 360,
        "marginTop": 0,
        "marginRight": "auto",
        "marginBottom": 0,
        "marginLeft": "auto"
    },
    "embed-480p": {
        "maxWidth": 854,
        "maxHeight": 480,
        "marginTop": 0,
        "marginRight": "auto",
        "marginBottom": 0,
        "marginLeft": "auto"
    },
    "embed-720p": {
        "maxWidth": 1280,
        "maxHeight": 720,
        "marginTop": 0,
        "marginRight": "auto",
        "marginBottom": 0,
        "marginLeft": "auto"
    },
    "embed-1080p": {
        "maxWidth": 1920,
        "maxHeight": 1080,
        "marginTop": 0,
        "marginRight": "auto",
        "marginBottom": 0,
        "marginLeft": "auto"
    }
});