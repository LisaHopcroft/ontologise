$(document).ready(function(){
	var load_file = "";

	$("#ontolog #toggle_src").click(function(){
		if ( load_file != "" ){
			txt_file = load_file.replace(/%5E/g,"").replace("04_VIS/trees/","02_TXT/").replace(".json","").replace(".txt_1",".txt").replace(".txt_2",".txt").replace(".txt_3",".txt");
			console.log( txt_file );
			$("#ontolog #src").empty();
			$("#ontolog #src").load( txt_file );

			$("#ontolog #display").children().hide();
			$("#ontolog #src").show();
		}
	});
	$("#ontolog #toggle_nav").click(function(){
		$("#ontolog #display").children().hide();
		$("#ontolog #nav").show();
	});
	$("#ontolog #nav a").click(function(){
		$("#graph").empty();
		$("#overlay").empty();
		$("#overlay").hide();
		load_file = $(this).attr('href')
		treeJson = d3.json(load_file, function(error, treeData) {
			dTree.init(treeData, {
				target: "#graph",
				debug: true,
				hideMarriageNodes: true,
				marriageNodeSize: 5,
	            height: 800,
	            width: 1200,
				callbacks: {
					nodeClick: function(name, extra) {
						alert('Click: ' + name);
					},
					nodeRightClick: function(name, extra) {
						alert('Right-click: ' + name);
					},
					textRenderer: function(name, extra, textClass) {
						if (extra && extra.nickname)
							name = name + " (" + extra.nickname + ")";
						return "<p align='center' class='" + textClass + "'>" + name + "</p>";
					},
					marriageClick: function(extra, id) {
						alert('Clicked marriage node' + id);
					},
					marriageRightClick: function(extra, id) {
						alert('Right-clicked marriage node' + id);
					},
				}
			});
		});
		return false;
	});
});
