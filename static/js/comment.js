$(function () {
    $(document).ready(function () {
        CKEDITOR.replace("commentbox");
    });
});

function quoteComment(comment_id, op) {
    $.ajax({
        type: "GET",
        url: "/get_comment",
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

        const editor = CKEDITOR.instances.commentbox;

        editor.focus();
        editor.setData("<blockquote>" + Comment.comment + "</blockquote><p></p>");
        editor.model.change((writer) => {
            writer.setSelection(writer.createPositionAt(editor.model.document.getRoot(), "end"));
        });
    }
}
