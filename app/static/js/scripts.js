$(function () {
    // for persisting the user input to the results page (old)
    // const url = new URLSearchParams(window.location.search);
    // const query = url.get('query');
    // const type = url.get('search-type');
    // if (query) $('#search-bar').val(query);
    // if (type) $('#type').val(type);


    // for setting the requests arg by the selected type
    function setSearchTypeArg() {
        const type = $("#search-type").find(":selected").text();
        $("#search-bar").attr("name", type.toLowerCase());
    }

    setSearchTypeArg();

    $("#search-type").change(function () {
        setSearchTypeArg();
    })

    $("#simple-search").submit(function () {
        setSearchTypeArg();
    })

    // Bootstrap tooltip
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
});
