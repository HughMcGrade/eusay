// Perform get request to 'url' and place the response inside 'div'
function performSetDivAjaxGetRequest(url, div) {
	$.ajax({
		type : "get",
		url : url,
		success : function(response) {
			$(div).html(response);
		},
		error : function(response) {
			alert("Request failed");
			// TODO improve error handling
			//console.log(response);
		}
	});
}

function voteUpProposal(proposalID, voteDiv) {
	performSetDivAjaxGetRequest("/vote_proposal/up/" + proposalID, voteDiv);
}

function voteDownProposal(proposalID, voteDiv) {
	performSetDivAjaxGetRequest("/vote_proposal/down/" + proposalID, voteDiv);
}

function setProposalVoteDiv(proposalID, voteDiv) {
	performSetDivAjaxGetRequest("/vote_proposal/get/" + proposalID, voteDiv);
}

function voteUpComment(commentID, voteDiv) {
	performSetDivAjaxGetRequest("/vote_comment/up/" + commentID, voteDiv);
}

function voteDownComment(commentID, voteDiv) {
	performSetDivAjaxGetRequest("/vote_comment/down/" + commentID, voteDiv);
}

function setCommentVotesDiv(commentID, voteDiv) {
	performSetDivAjaxGetRequest("/vote_comment/get/" + commentID, voteDiv);
}

// Post serialised 'form' (comments form) to 'postURL' and place the response inside 'commentDiv'
function setCommentPost(form, commentDiv, postURL) {
	var frm = $(form);
	frm.submit(function() {
		$.ajax({
			type : frm.attr('method'),
			url : postURL,
			data : frm.serialize(),
			success : function(response) {
				$(commentDiv).html(response);
			},
			error : function(response) {
				//console.log(response);
				$(commentDiv).html("Couldn't retrieve comments");
			}
		});
		return false;
	});
}

// Set comments ('commentDiv') and comments count('commentCountContainer') for field('field') on proposal ('proposalID') page
function setProposalCommentField(proposalID, field, commentDiv, commentCountContainer) {
	performSetDivAjaxGetRequest("/get_comments/" + proposalID + "/" + field, commentDiv);
	performSetDivAjaxGetRequest("/get_comments_count/" + proposalID + "/" + field, commentCountContainer);
}

// Create a new user (for the current session user) and reload the page
function createNewUser() {
	$.ajax({
		type : 'get',
		url : "/add_user/",
		success : function(response) {
			location.reload(true);
		},
		error : function(response) {
			location.reload(true);
		}
	});
}