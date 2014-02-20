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

function get_vote(proposal_id, vote_div) {
	$.ajax({
		type : "get",
		url : "/vote_proposal/get/" + proposal_id,
		success: function (data) {
			alert(data);
			//alert(vote_div);
			//console.log(data);
			$(vote_div).html(data);
		},
		error: function (data) {
			alert(data.responseText);
			console.log(data);
		}
	});	
}
function vote_down_proposal(proposal_id) {
	//$.get("/vote_proposal/down/" + proposal_id, function(data){location.reload(true);});
	$.ajax({
		type : "get",
		url : "/vote_proposal/down/" + proposal_id,
		success: function (data) {
			alert(data);
			console.log(data);
			$(vote_div).html(data);
		},
		error: function (data) {
			alert(data.responseText);
			console.log(data);
		}
	});	
}

function vote_up_comment(comment_id) {
	$.get("/vote_comment/up/" + comment_id, function(data){location.reload(true);});
}

function vote_down_comment(comment_id) {
	$.get("/vote_comment/down/" + comment_id, function(data){location.reload(true);});
}

function append_new_comment(div) {
	$(div).append("New comment!")
}

function post_comment(form, proposal_id, field, user_sid, comment_div) {
    var frm = $(form);
    console.log("hello");
    frm.submit(function () {
        $.ajax({
            type: frm.attr('method'),
            url: frm.attr('action'),
            data: frm.serialize(),
            success: function (data) {
            	console.log(data);
            	alert(data);
                $(comment_div).html(data);
            },
            error: function(data) {
            	console.log(data.responseText);
            	alert(data);
                $(comment_div).html("Something went wrong!");
            }
        });
        return false;
    });
}

/*function post_comment(proposal_id, field, text, user_sid, comment_div) {
	//alert("/post_comment/" + proposal_id + "/" + fieldObject.value + "?text=" + text + "&user_sid=" + user_sid);
	
	$.ajax({
                        url: "/post_comment/" + proposal_id + "/" + field,
                        data: { 'text' : text, 'user_sid' : user_sid },
                        dataType: 'post',
                        type: 'get',
                        success: function(json) {
                                append_new_comment(comment_div)
                        }
                });
	
	
	$.get("/post_comment/" + proposal_id + "/" + field, { 'text' : text, 'user_sid' : user_sid }, function(data)
	{
		$(fieldObject).append("New comment!")
		//location.reload(true);
	});
}*/