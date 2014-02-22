function vote_up_proposal(proposal_id, vote_div) {
	//$.get("/vote_proposal/up/" + proposal_id, function(data){location.reload(true);});
	$.ajax({
		type : "get",
		url : "/vote_proposal/up/" + proposal_id,
		success: function (data, textStatus, jqXHR) {
			//alert(data);
			//console.log(data);
			$(vote_div).html(data);
		},
		error: function (data) {
			alert(data.responseText);
			console.log(data);
		}
	});	
}

function vote_down_proposal(proposal_id, vote_div) {
	//$.get("/vote_proposal/down/" + proposal_id, function(data){location.reload(true);});
	$.ajax({
		type : "get",
		url : "/vote_proposal/down/" + proposal_id,
		success: function (data) {
			//console.log(data);
			$(vote_div).html(data);
		},
		error: function (data) {
			alert(data.responseText);
			console.log(data);
		}
	});	
}

function set_proposal_votes_div(proposal_id, vote_div) {
	$.ajax({
		type : "get",
		url : "/vote_proposal/get/" + proposal_id,
		success: function (data) {
			//console.log(data);
			$(vote_div).html(data);
		},
		error: function (data) {
			alert(data.responseText);
			console.log(data);
		}
	});	
}

function vote_up_comment(comment_id, vote_div) {
	//$.get("/vote_comment/up/" + comment_id, function(data){location.reload(true);});
	$.ajax({
		type : "get",
		url : "/vote_comment/up/" + comment_id,
		success: function (data) {
			//alert(data);
			//console.log(data);
			$(vote_div).html(data);
		},
		error: function (data) {
			alert(data.responseText);
			console.log(data);
		}
	});	
}

function vote_down_comment(comment_id, vote_div) {
	//$.get("/vote_comment/down/" + comment_id, function(data){location.reload(true);});
	$.ajax({
		type : "get",
		url : "/vote_comment/down/" + comment_id,
		success: function (data) {
			//alert(data);
			//console.log(data);
			$(vote_div).html(data);
		},
		error: function (data) {
			alert(data.responseText);
			console.log(data);
		}
	});
}

function set_comment_votes_div(comment_id, vote_div) {
	$.ajax({
		type : "get",
		url : "/vote_comment/get/" + comment_id,
		success: function (data) {
			//alert(data);
			//console.log(data);
			$(vote_div).html(data);
		},
		error: function (data) {
			alert(data.responseText);
			console.log(data);
		}
	});
}

function append_new_comment(div) {
	$(div).append("New comment!")
}

function set_comment_post(form, comment_div, post_url) {

    var frm = $(form);
    console.log("hello");
    frm.submit(function () {
        $.ajax({
            type: frm.attr('method'),
            url: /*frm.attr('action')*/ post_url,
            data: frm.serialize(),
            success: function (data) {
                $(comment_div).html(data);
            },
            error: function(data) {
            	console.log(data.responseText);
                $(comment_div).html("Couldn't retrieve comments");
            }
        });
        return false;
    });
}

function set_proposal_field_comments_div_and_count(proposal_id, field, comment_div, comment_count_container) {
      $.ajax({
          type: 'get',
          url: "/get_comments/" + proposal_id + "/" + field,
            success: function (data) {
                $(comment_div).html(data);
            },
            error: function(data) {
            	console.log(data);
                $(comment_div).html("Couldn't retrieve comments");
            }
      });
      $.ajax({
          type: 'get',
          url: "/get_comments_count/" + proposal_id + "/" + field,
            success: function (data) {
            	console.log(data);
                $(comment_count_container).html(data);
            },
            error: function(data) {
            	console.log(data);
                $(comment_count_container).html("Comments");
            }
      });
}

function new_user() {
	$.ajax({
          type: 'get',
          url: "/add_user/",
            success: function (data) {
            	location.reload(true);
            },
            error: function(data) {
            	location.reload(true);
            }
      });
}