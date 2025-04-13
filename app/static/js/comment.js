$(function () {
    window.CKEDITOR.replace("commentbox");
    $("table").addClass("table table-bordered table-sm");
});

function quoteComment(comment_id, op) {
    console.log("commenting...");
    $.ajax({
        type: "GET",
        url: "/api/get_comment",
        data: { comment_id: comment_id },
        contentType: "application/json",

        success: function (response) {
            _quote(JSON.parse(response), op);
        },

        error: function (XMLHttpRequest, textStatus, errorThrown) {
            console.log("XMLHttpRequest: " + XMLHttpRequest + "\nStatus: " + textStatus + "\nError: " + errorThrown);
        }
    });

    function _quote(Comment, op) {
        $("html, body").animate({ scrollTop: $(document).height() - $(window).height() });
        const editor = window.CKEDITOR.instances.commentbox;
        editor.insertHtml("<blockquote>" + Comment.comment + "</blockquote><br/>");
    }
}
