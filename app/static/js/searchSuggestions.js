$(function () {
    const loadingIconHtml = $("#loading-icon")[0].outerHTML;

    $("#search-bar").on({
        "input": async function () {
            const suggestionsBox = $("#suggestions-box");
            const inputWidth = $(this).outerWidth();
            suggestionsBox.width(inputWidth);

            const type = $("#search-type-dropdown option:selected").val();
            const query = $(this).val().toLowerCase();

            if (query.length > 0) {
                suggestionsBox.empty().show();
                suggestionsBox.append(loadingIconHtml);
            }

            //! one type at a time for now
            // TODO allow different and multiple parameters
            // TODO reuse search results route logic?
            const queryParameters = jQuery.param({ type, query });

            const response =
                await fetch("/api/search?" + queryParameters, {
                    method: "GET",
                    headers: {
                        'Content-Type': 'application/json; charset=utf-8'
                    },
                });

            const suggestions = await response.json();
            const length = Object.keys(suggestions).length;



            if (query.length > 0 && length > 0) {
                suggestionsBox.empty().show();
                suggestions.result.forEach(function (suggestion) {
                    const book = suggestion;
                    suggestionsBox.append("<div class='suggestion-item'>" + book[type] + "</div>");
                });
            } else {
                suggestionsBox.hide();
            }

            suggestionsBox.on("click", ".suggestion-item", function () {
                $("#search-bar").val($(this).text());
                suggestionsBox.hide();
            });

            $(document).on('click', function (event) {
                if (!$(event.target).closest("#search-bar-container").length) {
                    suggestionsBox.hide();
                }
            });
        }
    });
});
