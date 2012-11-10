google.load("visualization", "1.0", {"packages":["corechart"]});
google.setOnLoadCallback(update);

function update() {
    new Request.JSON({"url": "data/current", "onSuccess": redraw}).get();
}

function redraw(responseJSON, responseText) {
    draw_tasks("tasks_available", "Available tasks", responseJSON);
    draw_tasks("tasks_assigned", "Assigned tasks", responseJSON);
    draw_tasks("tasks_finished", "Finished tasks", responseJSON);
    draw_users("user_ranking", "User ranking", responseJSON);
}

function draw_tasks(id, title, data) {
    var gdata = new google.visualization.DataTable();
    gdata.addColumn("string", "URL shortener");
    gdata.addColumn("number", "Tasks");

    for (var service in data[id])
        gdata.addRow([service, data[id][service]]);

    var options = {"title": title};
    var chart = new google.visualization.PieChart(document.getElementById(id));
    chart.draw(gdata, options);
}

function draw_users(id, title, data) {
    var gdata = new google.visualization.DataTable();
    gdata.addColumn("string", "Username");
    gdata.addColumn("number", "Finished tasks");

    for (var user in data[id])
            gdata.addRow([user, data[id][user]]);

    var options = {"title": title};
    var chart = new google.visualization.BarChart(document.getElementById(id));
    chart.draw(gdata, options);
}
