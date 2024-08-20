var page = require('webpage').create(),
    system = require('system'),
    address, output, size;

function getElementByXpath(document, path) {
  	return document.evaluate(path, document, null, XPathResult.ANY_TYPE, null).singleNodeValue;
}


//var dur = 400000 // 400 seconds = 6m 40s // needs a long time for big map images...
//var portal_width = 13200 // map size - has to be super wide to chop off the zoom
//var portal_height = 4800 // map size
var dur = 6000 // 6 seconds
var portal_width = 4800 // document size
var portal_height = 2400 // document size

function click(el){
    var ev = document.createEvent("MouseEvent");
    ev.initMouseEvent(
        "click",
        true /* bubble */, true /* cancelable */,
        window, null,
        0, 0, 0, 0, /* coordinates */
        false, false, false, false, /* modifier keys */
        0 /*left*/, null
    );
    el.dispatchEvent(ev);
}

if (system.args.length < 3 || system.args.length > 5) {
    console.log('Usage: rasterize.js URL filename [paperwidth*paperheight|paperformat] [zoom]');
    console.log('  paper (pdf output) examples: "5in*7.5in", "10cm*20cm", "A4", "Letter"');
    console.log('  image (png/jpg output) examples: "1920px" entire page, window width 1920px');
    console.log('                                   "800px*600px" window, clipped to 800x600');
    phantom.exit(1);
}
else {
    address = system.args[1];
    output = system.args[2];
    page.viewportSize = { width: portal_width, height: portal_height };
    if (system.args.length > 3 && system.args[2].substr(-4) === ".pdf") {
        size = system.args[3].split('*');
        page.paperSize = size.length === 2 ? { width: size[0], height: size[1], margin: '0px' }
                                           : { format: system.args[3], orientation: 'portrait', margin: '1cm' };
    } else if (system.args.length > 3 && system.args[3].substr(-2) === "px") {
        size = system.args[3].split('*');
        if (size.length === 2) {
            pageWidth = parseInt(size[0], 10);
            pageHeight = parseInt(size[1], 10);
            page.viewportSize = { width: pageWidth, height: pageHeight };
            page.clipRect = { top: 0, left: 0, width: pageWidth, height: pageHeight };
        } else {
            console.log("size:", system.args[3]);
            pageWidth = parseInt(system.args[3], 10);
            pageHeight = parseInt(pageWidth * 3/4, 10); // it's as good an assumption as any
            console.log ("pageHeight:",pageHeight);
            page.viewportSize = { width: pageWidth, height: pageHeight };
        }
    }
    if (system.args.length > 4) {
        page.zoomFactor = system.args[4];
    }
    page.open(address, function (status) {
        if (status !== 'success') {
            console.log('Unable to load the address!');
            phantom.exit(1);
        } else {
			// render screenshot

			fullscreen_xpath = "/html/body/div[3]/div/div/section/div[2]/div/section/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div/div/div/div/div[3]/div[2]/div[2]/button";
			zoom_in_xpath = "/html/body/div[3]/div/div/section/div[2]/div/section/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div/div/div/div/div[1]/span[1]/span";

			document.getElementById('fullscreen_xpath').click();
			document.getElementById('zoom_in_xpath').click();
			document.getElementById('zoom_in_xpath').click();
			document.getElementById('zoom_in_xpath').click(); 

            window.setTimeout(function () {
                page.render(output);
                phantom.exit();
            }, dur);
        }
    });
}
