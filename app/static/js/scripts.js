$(function () {
    // for setting the requests arg by the selected type
    function setSearchTypeArg() {
        const type = $("#search-type-dropdown").find(":selected").text();
        $("#search-bar").attr("name", type.toLowerCase());
    }

    setSearchTypeArg();

    $("#search-type-dropdown").change(function () {
        setSearchTypeArg();
    });

    $("#simple-search").submit(function () {
        setSearchTypeArg();
    });

    // Bootstrap tooltip
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
});

$(function () {
    $("#order-btn").on({
        "click": function () {
            order = $("#order").val();
            if (order == "asc") {
                $("#order").val("desc");
                // console.log("changed to 'desc'");
            } else if (order == "desc") {
                $("#order").val("asc");
                // console.log("changed to 'asc'");
            }
            $("#sort-results").submit();
        }
    });
});
