var markdownpdf = require("markdown-pdf")
    , fs = require("fs")
   var options = {
     cssPath : "./github.css"
   }
    markdownpdf(options).from("../artifact/README.md").to("../README.pdf", function () {
	    console.log("Done!")
	})
