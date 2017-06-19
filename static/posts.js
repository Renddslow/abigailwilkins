$(function() {
	getPosts(page);

});

page = 1;

var getPosts = function(page) {
	$.ajax({
		type: "GET",
		url: "/feed?page=" + page,
		success: function(e) {
			for (var i = 0; i < e.length; i++) {
				displayPost(e[i]);
			}
		}
	});
};

var displayPost = function(content) {
	card = '<a href="/posts/' + content.id + '">'
	card += '<div post="' +  content.id +  '" class="card">';
	if (content.media != null) {
		card += '<div class="image-box" style="background-image: url(\'' + content.media + '\');"></div>';
	}
	card += '<div class="card-content"><p>' + content.content + '</p>';
	card += '<p class="date-posted">' + content.datePublished + '</p></div></div></a>';
	$(".posts").append($(card));
};
