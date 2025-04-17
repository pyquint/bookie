const bookActionsMsgDiv = $("#book-actions-msg-container");
const loadingIconHtml = $("#loading-icon")[0].outerHTML;
bookActionsMsgDiv.hide();

$(function () {
    const updateStatusForm = $("#update-status-form");

    // lots of thanks to:
    // https://pqina.nl/blog/async-form-posts-with-a-couple-lines-of-vanilla-javascript/

    updateStatusForm.on(
        "submit", async function (e) {
            e.preventDefault();
            const form = e.target;

            bookActionsMsgDiv.empty().show();
            bookActionsMsgDiv.append(loadingIconHtml);

            await fetch(form.action, {
                method: form.method,
                body: new FormData(form)
            });

            bookActionsMsgDiv.empty().show();
            bookActionsMsgDiv.append("<p>Status successfully updated!</p>");
        }
    );
});

async function toggleFavorite(bookID, userID) {
    console.log("toggle!");
    bookActionsMsgDiv.empty().show();
    bookActionsMsgDiv.append(loadingIconHtml);

    const request = await fetch("/toggle_favorite", {
        method: "POST",
        headers: { 'Content-Type': 'application/json; charset=utf-8' },
        body: JSON.stringify({ "book_id": bookID, "user_id": userID })
    });

    const response = await request.json();

    window.toggleFavIcon();

    bookActionsMsgDiv.empty().show();
    bookActionsMsgDiv.append("<p>" + response.message + "</p>");
};

