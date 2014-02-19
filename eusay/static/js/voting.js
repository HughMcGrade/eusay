function vote_up_proposal(proposal_id) {
	$.get("/vote_proposal/up/" + proposal_id, function(data){location.reload(true);});
}

function vote_down_proposal(proposal_id) {
	$.get("/vote_proposal/down/" + proposal_id, function(data){location.reload(true);});
	
}

function vote_up_comment(proposal_id) {
	$.get("/vote_comment/up/" + proposal_id, function(data){location.reload(true);});
}

function vote_down_comment(proposal_id) {
	$.get("/vote_comment/down/" + proposal_id, function(data){location.reload(true);});
}