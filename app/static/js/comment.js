$(function () {
    window.CKEDITOR.replace("commentbox");
    $("#comment-section table").addClass("table table-bordered table-sm");
});

function quote(comment_id) {
    $.ajax({
        type: "GET",
        url: "/api/comments/" + comment_id,
        contentType: "application/json",

        success: function (Comment) {
            $("html, body").animate({ scrollTop: $(document).height() - $(window).height() });
            const editor = window.CKEDITOR.instances.commentbox;
            editor.insertHtml("<blockquote>" + Comment.body + "</blockquote><br/>");
        },

        error: function (XMLHttpRequest, textStatus, errorThrown) {
            console.error("XMLHttpRequest: " + XMLHttpRequest);
            console.error("Status: " + textStatus);
            console.error("Error: " + errorThrown);
        }
    });
}
