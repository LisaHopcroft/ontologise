var page = require('webpage').create(),
    system = require('system');

if (system.args.length < 3 || system.args.length > 5) {
    console.log('Usage: rasterize.js URL filename [paperwidth*paperheight|paperformat] [zoom]');
    console.log('  paper (pdf output) examples: "5in*7.5in", "10cm*20cm", "A4", "Letter"');
    console.log('  image (png/jpg output) examples: "1920px" entire page, window width 1920px');
    console.log('                                   "800px*600px" window, clipped to 800x600');
    phantom.exit(1);
} 

var address = system.args[1];
var output = system.args[2];
page.viewportSize = { width: 6500, height: 4500 };

console.log('- Processing...');
console.log(address);

/*page.customHeaders = {'user-agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36', 'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,la;q=0.7', 'host': 'maps.nls.uk', 'connection': 'keep-alive'}; */

/* UPDATE 2020-04: NLS seems to be blocking phantomjs - can't get around it */

page.open(address, function (status) {
    if (status !== 'success') {
        console.log('Unable to load the address!');
        phantom.exit(1);
    } else {
		// render screenshot
        window.setTimeout(function () {
            page.render(output);
            phantom.exit();
        }, 200000); /* 200000 = 3.33 mins */
    }
});
