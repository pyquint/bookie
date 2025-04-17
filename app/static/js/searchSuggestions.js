$(function () {
    const loadingIconHtml = $("#loading-icon")[0].outerHTML;

    $("#search-bar").on(
        "input", async function () {
            const suggestionsBox = $("#suggestions-box");
            const inputWidth = $(this).outerWidth();
            suggestionsBox.width(inputWidth);

            const field = $("#search-type-dropdown option:selected").val();
            const query = $(this).val().toLowerCase();

            console.log("field: " + field);
            console.log("query: " + query);

            if (query.length > 0) {
                suggestionsBox.empty().show();
                suggestionsBox.append(loadingIconHtml);
            }

            // ! one type at a time for now
            // TODO allow different and multiple parameters
            // TODO reuse search results route logic?
            // ? above points done, I think?
            const queryParameters = jQuery.param({ field, query });

            const response =
                await fetch("/api/search?" + queryParameters, {
                    method: "GET",
                    headers: {
                        'Content-Type': 'application/json; charset=utf-8'
                    },
                });

            const responseJson = await response.json();
            const suggestions = responseJson.result;
            const length = Object.keys(suggestions).length;

            if (query.length > 0 && length > 0) {
                suggestionsBox.empty().show();
                suggestions.slice(0, 10).forEach(function (suggestion) {
                    const book = suggestion;
                    suggestionsBox.append("<div class='suggestion-item'>" + book[field] + "</div>");
                });
                suggestionsBox.append("<div class='suggestion-item' id='goto-search'><button id='search-for' type='submit'" +
                    "style='background:none; border:none; margin:0; padding:0; cursor: pointer;'> -> Search for '" + query + "'</button></div>");
            } else {
                suggestionsBox.hide();
            }

            suggestionsBox.on("click", ".suggestion-item", function () {
                if (!($(this).attr("id") == "goto-search")) {
                    $("#search-bar").val($(this).text());
                    suggestionsBox.hide();
                }
            });

            $(document).on(
                "click", function (event) {
                    if (!$(event.target).closest("#search-bar-container").length) {
                        suggestionsBox.hide();
                    }
                });
        }
    );
});
