$(function () {
    // for setting 2e requests arg by the selected type
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
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new window.bootstrap.Tooltip(tooltipTriggerEl));
});

$(function () {
    $("#order-btn").on({
        "click": function () {
            const order = $("#order").val();
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

    $("#sortby").on({
        "change": function () {
            const sortby = $("#sortby option:selected").val();
            $("#sort").val(sortby);
            $("#sort-results").submit();
        }
    });
});


