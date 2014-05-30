
var url = phantom.args[0];
var file_path = phantom.args[1];

var page = require('webpage').create();
page.open(url, function (status) {
	if(status !== 'success'){
		console.log('Unable to load the address!');
	}else{
		var pr = page.render(file_path);
		if(pr){
			console.log(file_path); // do not comment this line
		}
		phantom.exit();
    }
});