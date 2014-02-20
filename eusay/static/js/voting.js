function vote_up_proposal(proposal_id) {
	$.get("/vote_proposal/up/" + proposal_id, function(data){location.reload(true);});
}

function vote_down_proposal(proposal_id) {
	$.get("/vote_proposal/down/" + proposal_id, function(data){location.reload(true);});
	
}

function vote_up_comment(comment_id) {
	$.get("/vote_comment/up/" + comment_id, function(data){location.reload(true);});
}

function vote_down_comment(comment_id) {
	$.get("/vote_comment/down/" + comment_id, function(data){location.reload(true);});
}

function post_comment(proposal_id, field, text, user_sid) {
	$.get("/post_comment/" + proposal_id + "/" + field, { 'text' : text, 'user_sid' : user_sid }, function(data)
	{
		location.reload(true);
	});
}