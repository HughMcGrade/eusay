/*
// This could be used if the CSRF token is a problem
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}*/

// Perform get request to 'url' and place the response inside 'div'
function performSetDivAjaxGetRequest(url, div) {
    /*

    // This could be used if the CSRF token is a problem
    
    var csrftoken = $.cookie("csrftoken");

    $.ajaxSetup({
	crossDomain: false, // obviates need for sameOrigin test
	beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
		xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
	}
    });*/

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

// Reload 'commentsDiv' for proposal. For replies 'replyTo' should be non-null.
function reloadComments(commentDiv, proposal, replyTo) {
    if (replyTo == null) {
	var ajaxUrl = "/get_comments/" + proposal;
    }
    else {
	var ajaxUrl = "/get_comments/" + proposal + "/" + replyTo;
    }
    performSetDivAjaxGetRequest(ajaxUrl, commentDiv);
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
