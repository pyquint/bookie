$(function () {
    // for setting 2e requests arg by the selected type
    function setSearchTypeArg() {
        const type = $("#search-type-dropdown").find(":selected").text().toLowerCase();
        if (type != "all") {
            $("#search-bar").attr("name", type);
        }
    }

    setSearchTypeArg();

    $("#search-type-dropdown").on(
        "change", function () {
            setSearchTypeArg();
        });

    $("#simple-search").on(
        "submit", function () {
            setSearchTypeArg();
        });

    // Bootstrap tooltip
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new window.bootstrap.Tooltip(tooltipTriggerEl));
});

$(function () {
    $("#order-btn").on(
        "click", function () {
            const sortForm = $("#sort-results");
            sortForm.append("<input type='hidden' name='order' id='order' value='desc' />");
            const order = $("#order").val();
            if (order == "asc" || order == "") {
                $("#order").val("desc");
            } else if (order == "desc") {
                $("#order").val("asc");
            }
            $("#sort-results").trigger("submit");
        }
    );

    $("#sortby").on(
        "change", function () {
            const sortby = $("#sortby option:selected").val();
            $("#sort").val(sortby);
            $("#sort-results").trigger("submit");
        }
    );
});


