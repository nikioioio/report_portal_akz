anychart.onDocumentReady(function () {
    // create pie chart with passed data
    var chart = anychart.pie([
        ['Department Stores', 6371664],
        ['Discount Stores', 7216301],
        ['Men\'s/Women\'s Stores', 1486621],
        ['Juvenile Specialty Stores', 786622],
        ['All other outlets', 900000]
    ]);

    // set chart title text settings
    chart
        .title('ACME Corp. apparel sales through different retail channels')
        // create empty area in pie chart
        .innerRadius('40%');

    // set chart labels position to outside
    chart.labels().position('outside');

    // set container id for the chart
    chart.container('container');
    chart.background().fill({
        opacity: "0.0",
        mode: "fit"
    });

    // initiate chart drawing
    chart.draw();
});


anychart.onDocumentReady(function () {
    // create pie chart with passed data
    var chart = anychart.pie([
        ['Department Stores', 6371664],
        ['Discount Stores', 7216301],
        ['Men\'s/Women\'s Stores', 1486621],
        ['Juvenile Specialty Stores', 786622],
        ['All other outlets', 900000]
    ]);

    // set chart title text settings
    chart
        .title('ACME Corp. apparel sales through different retail channels')
        // create empty area in pie chart
        .innerRadius('40%');

    // set chart labels position to outside
    chart.labels().position('outside');

    // set container id for the chart
    chart.container('container');
    chart.background().fill({
        opacity: "0.0",
        mode: "fit"
    });
    // initiate chart drawing
    chart.draw();
});

