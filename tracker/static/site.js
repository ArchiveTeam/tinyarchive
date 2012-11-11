google.load("visualization", "1.0", {"packages":["corechart"]});
google.setOnLoadCallback(update);

function update() {
    new Request.JSON({"url": "data/", "onSuccess": redraw}).get();
}

function redraw(responseJSON, responseText) {
    draw_tasks("tasks_available", "Available tasks", responseJSON);
    draw_tasks("tasks_assigned", "Assigned tasks", responseJSON);
    draw_tasks("tasks_finished_day", "Finished tasks (24 hours)", responseJSON);
    draw_tasks("tasks_finished_alltime", "Finished tasks (all time)", responseJSON);
    draw_users("users_day", "Top 10 users (24 hours)", responseJSON);
    draw_users("users_alltime", "Top 10 users (all time)", responseJSON);
}

function draw_tasks(id, title, data) {
    var gdata = new google.visualization.DataTable();
    gdata.addColumn("string", "URL shortener");
    gdata.addColumn("number", "Tasks");

    for (var service in data[id])
        gdata.addRow([service, data[id][service]]);

    var options = {"title": title, "width": 450};
    var chart = new google.visualization.PieChart(document.getElementById(id));
    chart.draw(gdata, options);
}

function draw_users(id, title, data) {
    var gdata = google.visualization.arrayToDataTable(data[id]);

    var options = {
            "title": title,
            "isStacked": true,
            "height": 40 * (gdata.getNumberOfRows() + 1),
            legend: {position: "top"}
            };
    var chart = new google.visualization.BarChart(document.getElementById(id));
    chart.draw(gdata, options);
}
